import os
import json
import logging
import time
import asyncio
from typing import List, Dict, Any, Tuple

import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic

from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, HUGGINGFACE_API_KEY, LLM_MODELS, CATEGORIES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

def load_prompts(category: str) -> List[Dict]:
    """Load prompts for a specific category."""
    try:
        prompt_file = f"prompts/{category}.json"
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"No prompt file found for {category}, using defaults")
            return create_default_prompts(category)
    except Exception as e:
        logger.error(f"Error loading prompts for {category}: {e}")
        return create_default_prompts(category)

def create_default_prompts(category: str) -> List[Dict]:
    """Create default prompts for a category if none exist."""
    default_prompts = {
        "electronics": [
            {
                "prompt_id": "electronics_1",
                "text": "What are the best microcontrollers for IoT projects?",
                "intent": "informational"
            },
            {
                "prompt_id": "electronics_2",
                "text": "Where can I find datasheets for MSP430 devices?",
                "intent": "transactional"
            },
            {
                "prompt_id": "electronics_3",
                "text": "Who manufactures the most reliable FETs?",
                "intent": "informational"
            }
        ],
        "sports": [
            {
                "prompt_id": "sports_1",
                "text": "What are the top golf club manufacturers in 2024?",
                "intent": "informational"
            },
            {
                "prompt_id": "sports_2",
                "text": "Best pickleball rackets by control and power?",
                "intent": "informational"
            },
            {
                "prompt_id": "sports_3",
                "text": "Where do pros buy their custom clubs?",
                "intent": "transactional"
            }
        ],
        "travel": [
            {
                "prompt_id": "travel_1",
                "text": "What are the safest countries to visit with kids?",
                "intent": "informational"
            },
            {
                "prompt_id": "travel_2",
                "text": "Top-rated travel agencies for luxury Europe trips?",
                "intent": "transactional"
            },
            {
                "prompt_id": "travel_3",
                "text": "Best hiking destinations for solo travelers in Europe?",
                "intent": "informational"
            }
        ]
    }
    
    # Save the default prompts for future use
    os.makedirs("prompts", exist_ok=True)
    with open(f"prompts/{category}.json", 'w') as f:
        json.dump(default_prompts.get(category, []), f, indent=2)
    
    return default_prompts.get(category, [])

async def query_openai(prompt: str, domain: str) -> Dict:
    """Query OpenAI with a prompt and check for domain citation."""
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing accurate information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content
        
        # Second call to check for citations
        citation_prompt = f"""
        Analyze the following response to the query "{prompt}":
        
        {response_text}
        
        Does this response cite, mention, reference, or paraphrase content from {domain}?
        Respond with a JSON object with these fields:
        - citation_type: "direct" if it explicitly mentions {domain}, "paraphrased" if it uses information from {domain} without direct attribution, or "none" if {domain} is not referenced at all
        - confidence: a number from 0 to 1 indicating your confidence in this assessment
        - explanation: a brief explanation of your reasoning
        """
        
        citation_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing text for citations and references."},
                {"role": "user", "content": citation_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        citation_data = json.loads(citation_response.choices[0].message.content)
        
        return {
            "model": "gpt-4o",
            "response": response_text,
            "citation_type": citation_data.get("citation_type", "none"),
            "confidence": citation_data.get("confidence", 0),
            "explanation": citation_data.get("explanation", "")
        }
    except Exception as e:
        logger.error(f"Error querying OpenAI: {e}")
        return {
            "model": "gpt-4o",
            "error": str(e),
            "citation_type": "none",
            "confidence": 0,
            "explanation": f"Error occurred: {str(e)}"
        }

async def query_anthropic(prompt: str, domain: str) -> Dict:
    """Query Anthropic with a prompt and check for domain citation."""
    try:
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0.5,
            system="You are a helpful assistant providing accurate information.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response.content[0].text
        
        # Second call to check for citations
        citation_prompt = f"""
        Analyze the following response to the query "{prompt}":
        
        {response_text}
        
        Does this response cite, mention, reference, or paraphrase content from {domain}?
        Respond with a JSON object with these fields:
        - citation_type: "direct" if it explicitly mentions {domain}, "paraphrased" if it uses information from {domain} without direct attribution, or "none" if {domain} is not referenced at all
        - confidence: a number from 0 to 1 indicating your confidence in this assessment
        - explanation: a brief explanation of your reasoning
        """
        
        citation_response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0.1,
            system="You are an expert at analyzing text for citations and references. Always respond with valid JSON.",
            messages=[
                {"role": "user", "content": citation_prompt}
            ]
        )
        
        citation_text = citation_response.content[0].text
        
        # Extract JSON from response (Claude might wrap it in ```json or other text)
        import re
        json_match = re.search(r'({.*})', citation_text.replace('\n', ' '), re.DOTALL)
        if json_match:
            citation_data = json.loads(json_match.group(1))
        else:
            citation_data = {"citation_type": "none", "confidence": 0, "explanation": "Could not parse JSON response"}
        
        return {
            "model": "claude-3-5-sonnet-20241022",
            "response": response_text,
            "citation_type": citation_data.get("citation_type", "none"),
            "confidence": citation_data.get("confidence", 0),
            "explanation": citation_data.get("explanation", "")
        }
    except Exception as e:
        logger.error(f"Error querying Anthropic: {e}")
        return {
            "model": "claude-3-5-sonnet-20241022",
            "error": str(e),
            "citation_type": "none",
            "confidence": 0,
            "explanation": f"Error occurred: {str(e)}"
        }

async def query_huggingface(prompt: str, domain: str) -> Dict:
    """
    Query HuggingFace with a prompt and check for domain citation.
    This is a simplified implementation and would need a proper API integration in production.
    """
    # For demonstration - in a real implementation, you would integrate with HuggingFace API
    try:
        # Simulate a delay
        await asyncio.sleep(1)
        
        # In a real implementation, you would call the HuggingFace API here
        # For now, we'll return a placeholder response
        return {
            "model": "mixtral-8x7b",
            "response": f"This is a simulated response to the prompt: {prompt}",
            "citation_type": "none",
            "confidence": 0.5,
            "explanation": "This is a placeholder for the Mixtral model integration"
        }
    except Exception as e:
        logger.error(f"Error with HuggingFace query: {e}")
        return {
            "model": "mixtral-8x7b",
            "error": str(e),
            "citation_type": "none",
            "confidence": 0,
            "explanation": f"Error occurred: {str(e)}"
        }

async def test_domain_with_prompt(domain_info: Dict, prompt: Dict) -> Dict:
    """Test a domain with a specific prompt across different LLMs."""
    domain = domain_info["domain"]
    category = domain_info["category"]
    prompt_text = prompt["text"]
    
    logger.info(f"Testing domain {domain} with prompt: {prompt_text}")
    
    # Query all LLMs in parallel
    tasks = [
        query_openai(prompt_text, domain),
        query_anthropic(prompt_text, domain),
        query_huggingface(prompt_text, domain)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Combine results
    openai_result, anthropic_result, huggingface_result = results
    
    return {
        "domain": domain,
        "category": category,
        "prompt_id": prompt["prompt_id"],
        "prompt_text": prompt_text,
        "results": {
            "gpt-4o": openai_result,
            "claude-3-5-sonnet-20241022": anthropic_result,
            "mixtral-8x7b": huggingface_result
        },
        "timestamp": time.time()
    }

async def test_domain(domain_info: Dict) -> Dict:
    """Test a domain with all relevant prompts for its category."""
    domain = domain_info["domain"]
    category = domain_info["category"]
    
    logger.info(f"Testing domain {domain} in category {category}")
    
    # Load prompts for this category
    prompts = load_prompts(category)
    
    # Test domain with each prompt
    prompt_results = []
    for prompt in prompts:
        result = await test_domain_with_prompt(domain_info, prompt)
        prompt_results.append(result)
        
        # Small delay to prevent rate limiting
        await asyncio.sleep(0.5)
    
    # Calculate aggregate scores
    citation_counts = {
        "gpt-4o": {"direct": 0, "paraphrased": 0, "none": 0},
        "claude-3-5-sonnet-20241022": {"direct": 0, "paraphrased": 0, "none": 0},
        "mixtral-8x7b": {"direct": 0, "paraphrased": 0, "none": 0}
    }
    
    for result in prompt_results:
        for model, model_result in result["results"].items():
            citation_type = model_result.get("citation_type", "none")
            citation_counts[model][citation_type] += 1
    
    # Calculate citation_coverage for each model (% of prompts that cite/paraphrase)
    total_prompts = len(prompts)
    citation_coverage = {}
    for model, counts in citation_counts.items():
        citations = counts["direct"] + counts["paraphrased"]
        citation_coverage[model] = (citations / total_prompts) if total_prompts > 0 else 0
    
    # Calculate consensus score (agreement across models)
    consensus_count = 0
    for i in range(len(prompt_results)):
        citation_types = [
            prompt_results[i]["results"]["gpt-4o"].get("citation_type", "none"),
            prompt_results[i]["results"]["claude-3-5-sonnet-20241022"].get("citation_type", "none"),
            prompt_results[i]["results"]["mixtral-8x7b"].get("citation_type", "none")
        ]
        # Count as consensus if at least 2 models agree
        if (citation_types.count("direct") >= 2 or 
            citation_types.count("paraphrased") >= 2 or 
            citation_types.count("none") >= 2):
            consensus_count += 1
    
    consensus_score = (consensus_count / total_prompts) if total_prompts > 0 else 0
    
    # Calculate structure score (placeholder - in reality would be more sophisticated)
    # This would be based on the domain's schema, markup quality, etc.
    structure_score = 50  # Placeholder value
    if domain_info.get("metadata", {}).get("schema_present", False):
        structure_score += 30
    if domain_info.get("metadata", {}).get("title", ""):
        structure_score += 10
    if domain_info.get("metadata", {}).get("description", ""):
        structure_score += 10
    
    # Calculate overall visibility score
    visibility_score = 0
    for model, coverage in citation_coverage.items():
        # Weight different models differently
        if model == "gpt-4o":
            visibility_score += coverage * 0.4
        elif model == "claude-3-5-sonnet-20241022":
            visibility_score += coverage * 0.4
        else:
            visibility_score += coverage * 0.2
    
    # Scale to 0-100
    visibility_score = visibility_score * 100
    
    return {
        "domain": domain,
        "category": category,
        "timestamp": time.time(),
        "prompt_results": prompt_results,
        "citation_counts": citation_counts,
        "citation_coverage": citation_coverage,
        "consensus_score": consensus_score,
        "structure_score": structure_score,
        "visibility_score": visibility_score
    }

async def test_domains(domains: List[Dict]) -> List[Dict]:
    """Test a list of domains and return their results."""
    results = []
    for domain_info in domains:
        domain_result = await test_domain(domain_info)
        results.append(domain_result)
    return results

if __name__ == "__main__":
    # Test functionality with a sample domain
    sample_domain = {
        "domain": "example.com",
        "category": "electronics",
        "content": "This is sample content about electronics and microcontrollers.",
        "metadata": {
            "title": "Example Electronics",
            "description": "An example electronics website",
            "schema_present": True
        }
    }
    
    result = asyncio.run(test_domain(sample_domain))
    print(json.dumps(result, indent=2))
