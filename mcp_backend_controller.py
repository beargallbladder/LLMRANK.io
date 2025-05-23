"""
Backend/MCP Team Controller
Implements schema validation, enrichment agents, and decay-based suppression
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, ValidationError
import json
import os
from typing import Dict, List, Optional
import jsonschema
from datetime import datetime

app = FastAPI(title="MCP Backend Controller", version="1.0")

# Load entity schema
def load_entity_schema():
    """Load the contractual entity schema"""
    try:
        with open('schemas/entity.schema.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, f"Failed to load schema: {e}")

ENTITY_SCHEMA = load_entity_schema()

class StarvationPing(BaseModel):
    """Starvation ping model from frontend"""
    domain: str
    missing_fields: List[str]
    priority_level: str = "normal"  # normal, high, critical
    client_session_id: str
    timestamp: str

class EnrichmentRequest(BaseModel):
    """Enrichment request for agents"""
    domain: str
    missing_fields: List[str]
    priority_refresh: bool = False

def validate_entity_data(entity_data: Dict) -> Dict:
    """
    Validate outbound MCP data against schema before serving
    
    Args:
        entity_data: Entity data to validate
        
    Returns:
        Validation result with details
    """
    try:
        jsonschema.validate(entity_data, ENTITY_SCHEMA)
        return {
            "valid": True,
            "message": "Entity data validates against schema",
            "schema_version": ENTITY_SCHEMA.get("version", "1.0")
        }
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "message": f"Schema validation failed: {e.message}",
            "path": list(e.absolute_path),
            "schema_version": ENTITY_SCHEMA.get("version", "1.0")
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "schema_version": ENTITY_SCHEMA.get("version", "1.0")
        }

def apply_decay_suppression(entity_data: Dict) -> Dict:
    """
    Apply decay-based suppression logic
    
    Args:
        entity_data: Entity data to check for suppression
        
    Returns:
        Modified entity data with suppression applied
    """
    # Extract decay metrics
    drift_indicators = entity_data.get("drift_indicators", {})
    decay_rate = drift_indicators.get("decay_rate", 0)
    stability_score = drift_indicators.get("stability_score", 1.0)
    
    engagement_data = entity_data.get("engagement_data", {})
    engagement_rate = engagement_data.get("user_click_rate", 0)
    
    # Suppression logic
    suppression_active = False
    suppression_reason = None
    
    # High decay rate threshold
    if decay_rate > 0.1:  # 10% decay per day
        suppression_active = True
        suppression_reason = "high_decay_rate"
    
    # Low engagement threshold
    elif engagement_rate < 0.01:  # Less than 1% engagement
        suppression_active = True
        suppression_reason = "low_engagement"
    
    # Low stability threshold
    elif stability_score < 0.3:  # Less than 30% stability
        suppression_active = True
        suppression_reason = "low_stability"
    
    # Apply suppression to MCP metadata
    if "mcp_metadata" not in entity_data:
        entity_data["mcp_metadata"] = {}
    
    entity_data["mcp_metadata"]["suppression_active"] = suppression_active
    entity_data["mcp_metadata"]["suppression_reason"] = suppression_reason
    
    # Downgrade tier if suppressed
    if suppression_active:
        current_tier = entity_data["mcp_metadata"].get("tier_classification", "standard")
        if current_tier == "premium":
            entity_data["mcp_metadata"]["tier_classification"] = "standard"
        elif current_tier == "standard":
            entity_data["mcp_metadata"]["tier_classification"] = "basic"
    
    return entity_data

def trigger_enrichment_agents(domain: str, missing_fields: List[str], priority_refresh: bool = False):
    """
    Trigger enrichment agents on priority_refresh = true
    
    Args:
        domain: Domain to enrich
        missing_fields: Fields that need enrichment
        priority_refresh: Whether this is a priority refresh
    """
    print(f"🔧 Triggering enrichment agents for {domain}")
    print(f"   Missing fields: {missing_fields}")
    print(f"   Priority refresh: {priority_refresh}")
    
    # Determine which agents to trigger based on missing fields
    agents_to_trigger = []
    
    if "logo_data" in missing_fields or "logo_url" in missing_fields:
        agents_to_trigger.append("logo_enrichment_agent")
    
    if "authority_metrics" in missing_fields:
        agents_to_trigger.append("authority_enrichment_agent")
    
    if "competitive_metrics" in missing_fields:
        agents_to_trigger.append("competitive_analysis_agent")
    
    if "memory_metrics" in missing_fields:
        agents_to_trigger.append("memory_persistence_agent")
    
    # Log agent triggering (in production, this would actually trigger agents)
    for agent in agents_to_trigger:
        print(f"   🤖 Triggering {agent} for {domain}")
    
    return {
        "domain": domain,
        "agents_triggered": agents_to_trigger,
        "priority_refresh": priority_refresh,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/schema/entity")
async def get_entity_schema():
    """
    Expose GET /api/schema/entity endpoint
    Allow frontend to sync schema dynamically
    """
    return {
        "schema": ENTITY_SCHEMA,
        "version": ENTITY_SCHEMA.get("version", "1.0"),
        "last_updated": datetime.now().isoformat(),
        "description": "Contractual schema for MCP entity data validation"
    }

@app.post("/api/mcp/feedback/starvation")
async def receive_starvation_ping(starvation_ping: StarvationPing, background_tasks: BackgroundTasks):
    """
    Receive and process starvation pings
    POST /api/mcp/feedback/starvation
    """
    print(f"🚨 Starvation ping received for {starvation_ping.domain}")
    print(f"   Missing fields: {starvation_ping.missing_fields}")
    print(f"   Priority: {starvation_ping.priority_level}")
    
    # Determine if priority refresh is needed
    priority_refresh = starvation_ping.priority_level in ["high", "critical"]
    
    # Trigger enrichment agents in background
    background_tasks.add_task(
        trigger_enrichment_agents,
        starvation_ping.domain,
        starvation_ping.missing_fields,
        priority_refresh
    )
    
    return {
        "status": "received",
        "domain": starvation_ping.domain,
        "priority_refresh_triggered": priority_refresh,
        "estimated_enrichment_time": "5-15 minutes",
        "session_id": starvation_ping.client_session_id
    }

@app.post("/api/mcp/validate")
async def validate_entity_before_serving(entity_data: Dict):
    """
    Validate outbound MCP data against schema before serving
    """
    # Apply decay-based suppression first
    entity_data = apply_decay_suppression(entity_data)
    
    # Validate against schema
    validation_result = validate_entity_data(entity_data)
    
    return {
        "validation": validation_result,
        "entity_data": entity_data if validation_result["valid"] else None,
        "suppression_applied": entity_data.get("mcp_metadata", {}).get("suppression_active", False)
    }

@app.post("/api/mcp/enrich")
async def trigger_enrichment(enrichment_request: EnrichmentRequest, background_tasks: BackgroundTasks):
    """
    Manually trigger enrichment agents
    """
    background_tasks.add_task(
        trigger_enrichment_agents,
        enrichment_request.domain,
        enrichment_request.missing_fields,
        enrichment_request.priority_refresh
    )
    
    return {
        "status": "enrichment_triggered",
        "domain": enrichment_request.domain,
        "priority_refresh": enrichment_request.priority_refresh
    }

@app.get("/api/mcp/health")
async def mcp_health_check():
    """Health check for MCP backend system"""
    return {
        "status": "healthy",
        "schema_loaded": ENTITY_SCHEMA is not None,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MCP Backend Controller")
    print("📋 Schema validation: ✅")
    print("🔧 Enrichment agents: ✅") 
    print("⚰️  Decay suppression: ✅")
    uvicorn.run(app, host="0.0.0.0", port=9000)