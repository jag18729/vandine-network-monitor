#!/usr/bin/env python3
"""
MongoDB Service for Pi-hole Data Persistence and Export
Handles data serialization, storage, and export functionality
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId, json_util
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class MongoDBService:
    """MongoDB service for data persistence and export"""
    
    def __init__(self):
        mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.getenv('MONGO_DB_NAME', 'vandine_network')]
        
        # Collections
        self.queries = self.db['dns_queries']
        self.stats = self.db['pihole_stats']
        self.clients = self.db['network_clients']
        self.domains = self.db['domains']
        self.events = self.db['network_events']
        self.snapshots = self.db['system_snapshots']
        
    async def init_indexes(self):
        """Create database indexes for performance"""
        # DNS Queries indexes
        await self.queries.create_index([('timestamp', -1)])
        await self.queries.create_index([('domain', 1)])
        await self.queries.create_index([('client_ip', 1)])
        await self.queries.create_index([('blocked', 1)])
        
        # Stats indexes
        await self.stats.create_index([('timestamp', -1)])
        await self.stats.create_index([('type', 1)])
        
        # Clients indexes
        await self.clients.create_index([('ip_address', 1)], unique=True)
        await self.clients.create_index([('last_seen', -1)])
        
        # Domains indexes
        await self.domains.create_index([('domain', 1)], unique=True)
        await self.domains.create_index([('category', 1)])
        await self.domains.create_index([('threat_level', 1)])
        
    async def store_query(self, query_data: Dict[str, Any]) -> str:
        """Store DNS query data"""
        query_doc = {
            'timestamp': datetime.utcnow(),
            'domain': query_data.get('domain'),
            'client_ip': query_data.get('client_ip'),
            'client_name': query_data.get('client_name'),
            'query_type': query_data.get('query_type', 'A'),
            'blocked': query_data.get('blocked', False),
            'block_reason': query_data.get('block_reason'),
            'upstream': query_data.get('upstream'),
            'response_time': query_data.get('response_time'),
            'cache_hit': query_data.get('cache_hit', False)
        }
        
        result = await self.queries.insert_one(query_doc)
        
        # Update domain statistics
        await self.update_domain_stats(query_data['domain'], query_data.get('blocked', False))
        
        # Update client statistics
        await self.update_client_stats(query_data['client_ip'], query_data.get('client_name'))
        
        return str(result.inserted_id)
    
    async def update_domain_stats(self, domain: str, blocked: bool):
        """Update domain statistics"""
        await self.domains.update_one(
            {'domain': domain},
            {
                '$inc': {
                    'total_queries': 1,
                    'blocked_count': 1 if blocked else 0
                },
                '$set': {
                    'last_queried': datetime.utcnow()
                },
                '$setOnInsert': {
                    'first_seen': datetime.utcnow(),
                    'category': 'uncategorized'
                }
            },
            upsert=True
        )
    
    async def update_client_stats(self, ip: str, name: Optional[str] = None):
        """Update client statistics"""
        await self.clients.update_one(
            {'ip_address': ip},
            {
                '$inc': {'query_count': 1},
                '$set': {
                    'last_seen': datetime.utcnow(),
                    'hostname': name or ip
                },
                '$setOnInsert': {
                    'first_seen': datetime.utcnow(),
                    'device_type': 'unknown'
                }
            },
            upsert=True
        )
    
    async def store_pihole_stats(self, stats: Dict[str, Any]) -> str:
        """Store Pi-hole statistics snapshot"""
        stats_doc = {
            'timestamp': datetime.utcnow(),
            'type': 'pihole_summary',
            'data': {
                'queries_today': stats.get('dns_queries_today'),
                'blocked_today': stats.get('ads_blocked_today'),
                'percentage_blocked': stats.get('ads_percentage_today'),
                'unique_clients': stats.get('unique_clients'),
                'domains_on_blocklist': stats.get('domains_being_blocked'),
                'status': stats.get('status')
            }
        }
        
        result = await self.stats.insert_one(stats_doc)
        return str(result.inserted_id)
    
    async def get_query_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        client_ip: Optional[str] = None,
        domain: Optional[str] = None,
        blocked_only: bool = False,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get query history with filters"""
        
        query = {}
        
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter['$gte'] = start_time
            if end_time:
                time_filter['$lte'] = end_time
            query['timestamp'] = time_filter
        
        if client_ip:
            query['client_ip'] = client_ip
        
        if domain:
            query['domain'] = {'': domain, '': 'i'}
        
        if blocked_only:
            query['blocked'] = True
        
        cursor = self.queries.find(query).sort('timestamp', -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_top_domains(
        self,
        limit: int = 10,
        blocked: Optional[bool] = None,
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top queried/blocked domains"""
        
        pipeline = []
        
        # Time filter
        if start_time:
            pipeline.append({
                '$match': {'timestamp': {'$gte': start_time}}
            })
        
        # Blocked filter
        if blocked is not None:
            pipeline.append({
                '$match': {'blocked': blocked}
            })
        
        # Group and count
        pipeline.extend([
            {
                '$group': {
                    '_id': '$domain',
                    'count': {'$sum': 1},
                    'last_seen': {'$max': '$timestamp'}
                }
            },
            {'$sort': {'count': -1}},
            {'$limit': limit},
            {
                '$project': {
                    'domain': '$_id',
                    'count': 1,
                    'last_seen': 1,
                    '_id': 0
                }
            }
        ])
        
        return await self.queries.aggregate(pipeline).to_list(length=limit)
    
    async def get_client_stats(self) -> List[Dict[str, Any]]:
        """Get client statistics"""
        cursor = self.clients.find().sort('query_count', -1)
        return await cursor.to_list(length=100)
    
    async def export_data(
        self,
        collection: str,
        format: str = 'json',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """Export data in various formats"""
        
        # Build query
        query = {}
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter['$gte'] = start_time
            if end_time:
                time_filter['$lte'] = end_time
            query['timestamp'] = time_filter
        
        # Get collection
        coll = self.db[collection]
        
        # Fetch data
        cursor = coll.find(query)
        data = await cursor.to_list(length=None)
        
        # Format data
        if format == 'json':
            # Use json_util for BSON types
            return json.dumps(data, default=json_util.default, indent=2)
        
        elif format == 'csv':
            # Convert to DataFrame for CSV export
            df = pd.DataFrame(data)
            # Convert ObjectId to string
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
            return df.to_csv(index=False)
        
        elif format == 'jsonl':
            # JSON Lines format (one JSON object per line)
            lines = []
            for doc in data:
                lines.append(json.dumps(doc, default=json_util.default))
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def import_data(self, collection: str, data: str, format: str = 'json'):
        """Import data from various formats"""
        
        coll = self.db[collection]
        
        if format == 'json':
            # Parse JSON data
            docs = json.loads(data, object_hook=json_util.object_hook)
            if isinstance(docs, list):
                if docs:
                    await coll.insert_many(docs)
            else:
                await coll.insert_one(docs)
        
        elif format == 'jsonl':
            # Parse JSON Lines
            docs = []
            for line in data.strip().split('\n'):
                if line:
                    docs.append(json.loads(line, object_hook=json_util.object_hook))
            if docs:
                await coll.insert_many(docs)
        
        elif format == 'csv':
            # Parse CSV
            import io
            df = pd.read_csv(io.StringIO(data))
            docs = df.to_dict('records')
            if docs:
                await coll.insert_many(docs)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def create_snapshot(self, name: str, description: str = '') -> str:
        """Create a full system snapshot"""
        
        snapshot = {
            'timestamp': datetime.utcnow(),
            'name': name,
            'description': description,
            'data': {}
        }
        
        # Capture current stats
        collections_to_snapshot = ['queries', 'stats', 'clients', 'domains', 'events']
        
        for coll_name in collections_to_snapshot:
            coll = self.db[coll_name]
            # Get recent data (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            query = {'timestamp': {'$gte': yesterday}} if coll_name != 'clients' else {}
            
            data = await coll.find(query).to_list(length=10000)
            snapshot['data'][coll_name] = data
        
        # Store snapshot
        result = await self.snapshots.insert_one(snapshot)
        return str(result.inserted_id)
    
    async def restore_snapshot(self, snapshot_id: str):
        """Restore from a snapshot"""
        
        snapshot = await self.snapshots.find_one({'_id': ObjectId(snapshot_id)})
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        
        # Restore each collection
        for coll_name, data in snapshot['data'].items():
            coll = self.db[f"{coll_name}_restored"]
            # Clear existing data
            await coll.delete_many({})
            # Insert snapshot data
            if data:
                await coll.insert_many(data)
        
        return snapshot['name']
    
    async def get_analytics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Get comprehensive analytics"""
        
        # Calculate timeframe
        now = datetime.utcnow()
        if timeframe == '24h':
            start_time = now - timedelta(days=1)
        elif timeframe == '7d':
            start_time = now - timedelta(days=7)
        elif timeframe == '30d':
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)
        
        # Gather analytics
        analytics = {
            'timeframe': timeframe,
            'start_time': start_time,
            'end_time': now
        }
        
        # Query statistics
        query_count = await self.queries.count_documents({
            'timestamp': {'$gte': start_time}
        })
        
        blocked_count = await self.queries.count_documents({
            'timestamp': {'$gte': start_time},
            'blocked': True
        })
        
        unique_domains = await self.queries.distinct('domain', {
            'timestamp': {'$gte': start_time}
        })
        
        unique_clients = await self.queries.distinct('client_ip', {
            'timestamp': {'$gte': start_time}
        })
        
        analytics['summary'] = {
            'total_queries': query_count,
            'blocked_queries': blocked_count,
            'block_rate': (blocked_count / query_count * 100) if query_count > 0 else 0,
            'unique_domains': len(unique_domains),
            'unique_clients': len(unique_clients)
        }
        
        # Top domains
        analytics['top_queried'] = await self.get_top_domains(10, None, start_time)
        analytics['top_blocked'] = await self.get_top_domains(10, True, start_time)
        
        # Client activity
        client_activity = await self.queries.aggregate([
            {'': {'timestamp': {'$gte': start_time}}},
            {
                '$group': {
                    '_id': '$client_ip',
                    'queries': {'$sum': 1},
                    'blocked': {
                        '$sum': {'$cond': ['$blocked', 1, 0]}
                    }
                }
            },
            {'$sort': {'queries': -1}},
            {'$limit': 10}
        ]).to_list(length=10)
        
        analytics['client_activity'] = client_activity
        
        return analytics

# FastAPI endpoints for MongoDB service
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

app = FastAPI(title="MongoDB Data Service", version="1.0.0")
db_service = MongoDBService()

class ExportRequest(BaseModel):
    collection: str
    format: str = 'json'
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ImportRequest(BaseModel):
    collection: str
    format: str = 'json'
    data: str

class SnapshotRequest(BaseModel):
    name: str
    description: str = ''

@app.on_event("startup")
async def startup():
    await db_service.init_indexes()

@app.get("/api/data/export/{collection}")
async def export_collection(
    collection: str,
    format: str = Query('json', enum=['json', 'csv', 'jsonl']),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export collection data in specified format"""
    try:
        start_time = datetime.fromisoformat(start_date) if start_date else None
        end_time = datetime.fromisoformat(end_date) if end_date else None
        
        data = await db_service.export_data(collection, format, start_time, end_time)
        
        # Set appropriate content type
        if format == 'csv':
            media_type = 'text/csv'
            filename = f"{collection}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        elif format == 'jsonl':
            media_type = 'application/x-ndjson'
            filename = f"{collection}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        else:
            media_type = 'application/json'
            filename = f"{collection}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return Response(
            content=data,
            media_type=media_type,
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/import")
async def import_data(request: ImportRequest):
    """Import data into collection"""
    try:
        await db_service.import_data(request.collection, request.data, request.format)
        return {"status": "success", "message": f"Data imported to {request.collection}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/analytics")
async def get_analytics(timeframe: str = Query('24h', enum=['24h', '7d', '30d'])):
    """Get analytics for specified timeframe"""
    try:
        analytics = await db_service.get_analytics(timeframe)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/snapshot")
async def create_snapshot(request: SnapshotRequest):
    """Create system snapshot"""
    try:
        snapshot_id = await db_service.create_snapshot(request.name, request.description)
        return {
            "status": "success",
            "snapshot_id": snapshot_id,
            "name": request.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/snapshot/{snapshot_id}/restore")
async def restore_snapshot(snapshot_id: str):
    """Restore from snapshot"""
    try:
        name = await db_service.restore_snapshot(snapshot_id)
        return {
            "status": "success",
            "message": f"Restored snapshot: {name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/queries")
async def get_queries(
    client_ip: Optional[str] = None,
    domain: Optional[str] = None,
    blocked_only: bool = False,
    limit: int = Query(100, le=1000)
):
    """Get DNS query history"""
    try:
        queries = await db_service.get_query_history(
            client_ip=client_ip,
            domain=domain,
            blocked_only=blocked_only,
            limit=limit
        )
        return {"queries": queries, "count": len(queries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/clients")
async def get_clients():
    """Get client statistics"""
    try:
        clients = await db_service.get_client_stats()
        return {"clients": clients, "count": len(clients)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mongodb-data"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8890)
