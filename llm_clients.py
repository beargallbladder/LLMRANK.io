"""
PRD-25: LLM Model Enrichment & Signal Divergence Indexing (Purity25)

LLM Clients
----------
This module provides clients for interacting with various LLM providers.
"""

import os
import json
import logging
import time
import random
import requests
from typing import Dict, List, Optional, Any, Union

# OpenAI client
from openai import OpenAI

# Anthropic client
import anthropic
from anthropic import Anthropic

# Import Google Gemini API
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    """Base class for LLM clients."""
    
    def __init__(self, model_name: str):
        """Initialize the LLM client."""
        self.model_name = model_name
    
    def extract_domains(self, text: str) -> List[str]:
        """
        Extract domain names from text.
        
        Args:
            text: The text to extract domains from
            
        Returns:
            List of domain names
        """
        # Simple domain extraction logic
        words = text.split()
        domains = []
        
        for word in words:
            # Clean up punctuation
            word = word.strip(",.;:()[]{}\"'")
            
            # Check if word looks like a domain
            if ("." in word and 
                not word.startswith("http") and 
                not word.endswith(".") and
                "/" not in word and
                len(word) > 3):
                domains.append(word.lower())
        
        return list(set(domains))  # Remove duplicates

class OpenAIClient(LLMClient):
    """Client for OpenAI models."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the OpenAI client."""
        super().__init__(model_name)
        
        # Initialize OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        logger.info(f"Initialized OpenAI client with model: {model_name}")
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the OpenAI model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response text
        """
        try:
            logger.info(f"Generating response using OpenAI {self.model_name}")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. When asked about websites or online resources, always include the full domain name (e.g., example.com) in your response."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            return f"Error: {e}"
    
    def extract_cited_domains(self, prompt: str) -> List[str]:
        """
        Extract domains cited by the model for a given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            List of domains cited in the response
        """
        response_text = self.generate_response(prompt)
        domains = self.extract_domains(response_text)
        
        logger.info(f"OpenAI {self.model_name} cited {len(domains)} domains: {domains}")
        return domains

class AnthropicClient(LLMClient):
    """Client for Anthropic models."""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """Initialize the Anthropic client."""
        super().__init__(model_name)
        
        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.client = Anthropic(api_key=api_key)
        
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        logger.info(f"Initialized Anthropic client with model: {model_name}")
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the Anthropic model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response text
        """
        try:
            logger.info(f"Generating response using Anthropic {self.model_name}")
            
            response = self.client.messages.create(
                model=self.model_name,
                system="You are a helpful assistant. When asked about websites or online resources, always include the full domain name (e.g., example.com) in your response.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating response with Anthropic: {e}")
            return f"Error: {e}"
    
    def extract_cited_domains(self, prompt: str) -> List[str]:
        """
        Extract domains cited by the model for a given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            List of domains cited in the response
        """
        response_text = self.generate_response(prompt)
        domains = self.extract_domains(response_text)
        
        logger.info(f"Anthropic {self.model_name} cited {len(domains)} domains: {domains}")
        return domains

class GeminiClient(LLMClient):
    """Client for Google Gemini models."""
    
    def __init__(self, model_name: str = "models/gemini-1.5-pro"):
        """Initialize the Gemini client."""
        super().__init__(model_name)
        
        # Initialize Gemini client
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Get the model
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Initialized Gemini client with model: {model_name}")
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the Gemini model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response text
        """
        try:
            logger.info(f"Generating response using Gemini {self.model_name}")
            
            response = self.model.generate_content(
                [
                    "You are a helpful assistant. When asked about websites or online resources, always include the full domain name (e.g., example.com) in your response.",
                    prompt
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return f"Error: {e}"
    
    def extract_cited_domains(self, prompt: str) -> List[str]:
        """
        Extract domains cited by the model for a given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            List of domains cited in the response
        """
        response_text = self.generate_response(prompt)
        domains = self.extract_domains(response_text)
        
        logger.info(f"Gemini {self.model_name} cited {len(domains)} domains: {domains}")
        return domains

class MockClient(LLMClient):
    """Mock client for testing."""
    
    def __init__(self, model_name: str):
        """Initialize the mock client."""
        super().__init__(model_name)
        
        # Mock data for testing
        self.mock_data = {
            "gpt-4": ["example.com", "ai-research.org", "techblog.io", "gpt4-exclusive.com"],
            "claude": ["example.com", "datascience.net", "ai-research.org", "claude-exclusive.net"],
            "mixtral": ["example.com", "machinelearning.dev", "devops.co", "mixtral-exclusive.io"],
            "gemini": ["example.com", "ai-research.org", "cybersecurity.io", "gemini-exclusive.org"],
            "cohere": ["example.com", "ai-research.org", "knowledge-base.io", "cohere-exclusive.com"],
            "llama-3": ["example.com", "open-source.org", "research-papers.net", "llama-exclusive.ai"],
            "perplexity": ["example.com", "ai-research.org", "real-time-data.io", "perplexity-exclusive.co"],
            "claude-3-opus": ["example.com", "advanced-research.org", "deep-insights.ai", "opus-exclusive.org"]
        }
        
        logger.info(f"Initialized mock client with model: {model_name}")
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a mock response.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            A mock response text
        """
        logger.info(f"Generating mock response for {self.model_name}")
        
        # Mock delay for realism
        time.sleep(random.uniform(0.2, 1.0))
        
        domains = self.mock_data.get(self.model_name, ["example.com"])
        
        response = f"Here's a response about {', '.join(domains)}. These are the top sites in this field."
        return response
    
    def extract_cited_domains(self, prompt: str) -> List[str]:
        """
        Return mock domains for testing.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            List of mock domains
        """
        domains = self.mock_data.get(self.model_name, ["example.com"])
        
        logger.info(f"Mock {self.model_name} cited {len(domains)} domains: {domains}")
        return domains

class DeepSeekClient(LLMClient):
    """Client for DeepSeek models."""
    
    def __init__(self, model_name: str = "deepseek-chat"):
        """Initialize the DeepSeek client."""
        super().__init__(model_name)
        
        # Initialize DeepSeek client
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        # DeepSeek API endpoint
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        logger.info(f"Initialized DeepSeek client with model: {model_name}")
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the DeepSeek model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response text
        """
        try:
            logger.info(f"Generating response using DeepSeek {self.model_name}")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. When asked about websites or online resources, always include the full domain name (e.g., example.com) in your response."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating response with DeepSeek: {e}")
            return f"Error: {e}"
    
    def extract_cited_domains(self, prompt: str) -> List[str]:
        """
        Extract domains cited by the model for a given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            List of domains cited in the response
        """
        response_text = self.generate_response(prompt)
        domains = self.extract_domains(response_text)
        
        logger.info(f"DeepSeek {self.model_name} cited {len(domains)} domains: {domains}")
        return domains

class MultiModelClient:
    """Client for interacting with multiple LLM models."""
    
    def __init__(self, use_real_models: bool = True):
        """
        Initialize the multi-model client.
        
        Args:
            use_real_models: Whether to use real models or mock clients
        """
        self.use_real_models = use_real_models
        
        # Initialize individual clients
        if use_real_models:
            try:
                self.openai_client = OpenAIClient()
                logger.info("Initialized OpenAI client")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                self.openai_client = MockClient("gpt-4")
            
            try:
                self.anthropic_client = AnthropicClient()
                logger.info("Initialized Anthropic client")
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {e}")
                self.anthropic_client = MockClient("claude")
            
            try:
                self.gemini_client = GeminiClient()
                logger.info("Initialized Gemini client")
            except Exception as e:
                logger.error(f"Error initializing Gemini client: {e}")
                self.gemini_client = MockClient("gemini")
            
            try:
                self.deepseek_client = DeepSeekClient()
                logger.info("Initialized DeepSeek client")
            except Exception as e:
                logger.error(f"Error initializing DeepSeek client: {e}")
                self.deepseek_client = MockClient("deepseek")
            
            # For models we don't have API access to, use mocks
            self.mixtral_client = MockClient("mixtral")
            self.cohere_client = MockClient("cohere")
            self.llama_client = MockClient("llama-3")
            self.perplexity_client = MockClient("perplexity")
            self.claude_opus_client = MockClient("claude-3-opus")
        else:
            # Use all mock clients for testing
            self.openai_client = MockClient("gpt-4")
            self.anthropic_client = MockClient("claude")
            self.gemini_client = MockClient("gemini")
            self.deepseek_client = MockClient("deepseek")
            self.mixtral_client = MockClient("mixtral")
            self.cohere_client = MockClient("cohere")
            self.llama_client = MockClient("llama-3")
            self.perplexity_client = MockClient("perplexity")
            self.claude_opus_client = MockClient("claude-3-opus")
        
        # Map of model names to clients
        self.clients = {
            "gpt-4": self.openai_client,
            "claude": self.anthropic_client,
            "gemini": self.gemini_client,
            "deepseek": self.deepseek_client,
            "mixtral": self.mixtral_client,
            "cohere": self.cohere_client,
            "llama-3": self.llama_client,
            "perplexity": self.perplexity_client,
            "claude-3-opus": self.claude_opus_client
        }
        
        logger.info(f"Initialized multi-model client with {len(self.clients)} models")
    
    def get_all_model_responses(self, prompt: str) -> Dict[str, List[str]]:
        """
        Get responses from all models for a given prompt.
        
        Args:
            prompt: The prompt to send to the models
            
        Returns:
            Dictionary of model responses (model name -> list of domains cited)
        """
        logger.info(f"Getting responses from all models for prompt: {prompt[:50]}...")
        
        responses = {}
        
        for model_name, client in self.clients.items():
            try:
                domains = client.extract_cited_domains(prompt)
                responses[model_name] = domains
            except Exception as e:
                logger.error(f"Error getting response from {model_name}: {e}")
                responses[model_name] = []
        
        return responses
    
    def get_model_response(self, model_name: str, prompt: str) -> List[str]:
        """
        Get response from a specific model for a given prompt.
        
        Args:
            model_name: The name of the model to use
            prompt: The prompt to send to the model
            
        Returns:
            List of domains cited in the response
        """
        if model_name not in self.clients:
            logger.error(f"Unknown model: {model_name}")
            return []
        
        client = self.clients[model_name]
        return client.extract_cited_domains(prompt)

def test_multi_model_client():
    """Test the multi-model client."""
    logger.info("Testing multi-model client")
    
    # Initialize client with mock models
    client = MultiModelClient(use_real_models=False)
    
    # Test prompt
    test_prompt = "What are the top AI research websites?"
    
    # Get responses from all models
    responses = client.get_all_model_responses(test_prompt)
    
    logger.info(f"Responses from all models: {json.dumps(responses, indent=2)}")
    
    return responses

if __name__ == "__main__":
    logger.info("Running LLM clients test")
    
    # Test the multi-model client
    test_results = test_multi_model_client()
    
    logger.info(f"Test results: {json.dumps(test_results, indent=2)}")