"""
Multi-LLM Arena: Competitive Model Battle System
Codename: "Model Gladiator Arena"

This system creates a competitive environment where models battle for supremacy.
DeepSeek R1 starts as the defending champion, all others try to outseat it.
Customer engagement and insight quality determine the ultimate winner.
"""

import json
import time
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
import openai
import anthropic

# LLM Client Configurations
class LLMClients:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # DeepSeek configuration (assuming DeepSeek uses OpenAI-compatible API)
        self.deepseek_client = openai.OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY', ''),
            base_url="https://api.deepseek.com/v1"  # DeepSeek API endpoint
        )
        
        # Model configurations with battle stats
        self.models = {
            'deepseek-r1': {
                'client': 'deepseek',
                'name': 'DeepSeek R1',
                'status': 'champion',  # Starts as defending champion
                'cost_per_1k': 0.0001,  # Ultra cheap
                'battle_wins': 0,
                'battle_losses': 0,
                'quality_avg': 0.0,
                'engagement_score': 0.0,
                'total_insights': 0
            },
            'gpt-4o': {
                'client': 'openai',
                'name': 'GPT-4o',
                'status': 'challenger',
                'cost_per_1k': 0.03,
                'battle_wins': 0,
                'battle_losses': 0,
                'quality_avg': 0.0,
                'engagement_score': 0.0,
                'total_insights': 0
            },
            'claude-3-5-sonnet-20241022': {
                'client': 'anthropic',
                'name': 'Claude 3.5 Sonnet',
                'status': 'challenger',
                'cost_per_1k': 0.025,
                'battle_wins': 0,
                'battle_losses': 0,
                'quality_avg': 0.0,
                'engagement_score': 0.0,
                'total_insights': 0
            },
            'gpt-4o-mini': {
                'client': 'openai',
                'name': 'GPT-4o Mini',
                'status': 'challenger',
                'cost_per_1k': 0.0015,
                'battle_wins': 0,
                'battle_losses': 0,
                'quality_avg': 0.0,
                'engagement_score': 0.0,
                'total_insights': 0
            }
        }

class ModelArena:
    """
    Competitive arena where models battle for the right to be primary.
    Tracks performance, engagement, and cost efficiency.
    """
    
    def __init__(self):
        self.clients = LLMClients()
        self.arena_data_file = 'data/arena_battles.json'
        self.engagement_data_file = 'data/engagement_metrics.json'
        self.load_arena_data()
        
    def load_arena_data(self):
        """Load existing arena battle data"""
        try:
            with open(self.arena_data_file, 'r') as f:
                arena_data = json.load(f)
                # Update model stats from saved data
                for model_id, stats in arena_data.get('models', {}).items():
                    if model_id in self.clients.models:
                        self.clients.models[model_id].update(stats)
        except FileNotFoundError:
            self.save_arena_data()
    
    def save_arena_data(self):
        """Save arena battle data"""
        os.makedirs('data', exist_ok=True)
        arena_data = {
            'models': self.clients.models,
            'last_updated': time.time(),
            'arena_version': '1.0'
        }
        with open(self.arena_data_file, 'w') as f:
            json.dump(arena_data, f, indent=2)

    async def generate_insight(self, model_id: str, domain: str, content: str) -> Dict:
        """
        Generate insight using specified model
        
        Args:
            model_id: Model identifier (e.g., 'deepseek-r1', 'gpt-4o')
            domain: Domain being analyzed
            content: Content to analyze
            
        Returns:
            Insight data with metadata
        """
        model_config = self.clients.models[model_id]
        
        prompt = f"""
        Analyze this brand's digital presence and competitive positioning:
        
        Domain: {domain}
        Content: {content}
        
        Provide a comprehensive competitive intelligence insight that covers:
        1. Brand positioning and market perception
        2. Key differentiators and unique value propositions
        3. Competitive advantages and potential vulnerabilities
        4. Memory hooks and brand recall factors
        
        Be specific, actionable, and insightful. Focus on competitive intelligence value.
        """
        
        try:
            start_time = time.time()
            
            if model_config['client'] == 'openai':
                response = self.clients.openai_client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.7
                )
                insight_text = response.choices[0].message.content
                
            elif model_config['client'] == 'deepseek':
                response = self.clients.deepseek_client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.7
                )
                insight_text = response.choices[0].message.content
                
            elif model_config['client'] == 'anthropic':
                # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
                response = self.clients.anthropic_client.messages.create(
                    model=model_id,
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                insight_text = response.content[0].text
            
            processing_time = time.time() - start_time
            
            # Calculate quality score based on insight characteristics
            quality_score = self.calculate_quality_score(insight_text, domain)
            
            insight_data = {
                'id': f"{model_id}_{domain}_{int(time.time())}",
                'model': model_id,
                'model_name': model_config['name'],
                'domain': domain,
                'content': insight_text,
                'quality_score': quality_score,
                'processing_time': processing_time,
                'timestamp': time.time(),
                'cost_estimate': len(insight_text) * model_config['cost_per_1k'] / 1000,
                'status': 'active'
            }
            
            # Update model stats
            self.update_model_performance(model_id, quality_score)
            
            return insight_data
            
        except Exception as e:
            print(f"Error generating insight with {model_id}: {e}")
            return {
                'id': f"error_{model_id}_{int(time.time())}",
                'model': model_id,
                'domain': domain,
                'content': f"Error generating insight: {str(e)}",
                'quality_score': 0.0,
                'timestamp': time.time(),
                'status': 'error'
            }

    def calculate_quality_score(self, insight_text: str, domain: str) -> float:
        """
        Calculate quality score for an insight
        
        Args:
            insight_text: Generated insight content
            domain: Domain being analyzed
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Length and depth (0-0.3)
        if len(insight_text) > 200:
            score += 0.1
        if len(insight_text) > 400:
            score += 0.1
        if len(insight_text) > 600:
            score += 0.1
            
        # Competitive intelligence keywords (0-0.4)
        competitive_keywords = [
            'competitive advantage', 'market position', 'differentiat', 
            'unique value', 'brand perception', 'market share',
            'competitor', 'positioning', 'strategic', 'advantage'
        ]
        
        keyword_score = 0
        for keyword in competitive_keywords:
            if keyword.lower() in insight_text.lower():
                keyword_score += 0.1
        score += min(keyword_score, 0.4)
        
        # Domain relevance (0-0.2)
        domain_clean = domain.replace('.com', '').replace('.', ' ')
        if domain_clean.lower() in insight_text.lower():
            score += 0.1
        if 'brand' in insight_text.lower():
            score += 0.1
            
        # Actionability indicators (0-0.1)
        actionable_words = ['should', 'can', 'opportunity', 'recommend', 'strategy']
        if any(word in insight_text.lower() for word in actionable_words):
            score += 0.1
            
        return min(score, 1.0)

    def update_model_performance(self, model_id: str, quality_score: float):
        """Update model performance metrics"""
        model = self.clients.models[model_id]
        
        # Update running averages
        total_insights = model['total_insights']
        current_avg = model['quality_avg']
        
        # Calculate new average
        new_total = total_insights + 1
        new_avg = ((current_avg * total_insights) + quality_score) / new_total
        
        model['quality_avg'] = new_avg
        model['total_insights'] = new_total
        
        self.save_arena_data()

    async def battle_round(self, domain: str, content: str) -> Dict:
        """
        Run a battle round between all models
        
        Args:
            domain: Domain to analyze
            content: Content to analyze
            
        Returns:
            Battle results with winner
        """
        print(f"🥊 ARENA BATTLE: {domain}")
        print("=" * 50)
        
        # Generate insights from all available models
        battle_results = {}
        
        for model_id in self.clients.models.keys():
            try:
                insight = await self.generate_insight(model_id, domain, content)
                battle_results[model_id] = insight
                
                model_name = self.clients.models[model_id]['name']
                quality = insight['quality_score']
                print(f"🤖 {model_name}: Quality {quality:.3f}")
                
            except Exception as e:
                print(f"❌ {model_id} failed: {e}")
                battle_results[model_id] = {
                    'quality_score': 0.0,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Determine winner
        winner = max(battle_results.keys(), 
                    key=lambda k: battle_results[k].get('quality_score', 0))
        
        winner_quality = battle_results[winner]['quality_score']
        winner_name = self.clients.models[winner]['name']
        
        print(f"🏆 WINNER: {winner_name} (Quality: {winner_quality:.3f})")
        
        # Update battle stats
        self.update_battle_stats(winner, list(battle_results.keys()))
        
        # Return the winning insight for production use
        return {
            'winner': winner,
            'winner_insight': battle_results[winner],
            'all_results': battle_results,
            'battle_summary': {
                'domain': domain,
                'winner': winner_name,
                'winner_quality': winner_quality,
                'timestamp': time.time()
            }
        }

    def update_battle_stats(self, winner: str, participants: List[str]):
        """Update win/loss records for all participants"""
        for model_id in participants:
            if model_id == winner:
                self.clients.models[model_id]['battle_wins'] += 1
            else:
                self.clients.models[model_id]['battle_losses'] += 1
        
        self.save_arena_data()

    def get_arena_leaderboard(self) -> List[Dict]:
        """Get current arena leaderboard"""
        leaderboard = []
        
        for model_id, stats in self.clients.models.items():
            total_battles = stats['battle_wins'] + stats['battle_losses']
            win_rate = stats['battle_wins'] / total_battles if total_battles > 0 else 0
            
            leaderboard.append({
                'model_id': model_id,
                'name': stats['name'],
                'status': stats['status'],
                'win_rate': win_rate,
                'quality_avg': stats['quality_avg'],
                'total_insights': stats['total_insights'],
                'battle_wins': stats['battle_wins'],
                'battle_losses': stats['battle_losses'],
                'cost_per_1k': stats['cost_per_1k']
            })
        
        # Sort by win rate, then by quality average
        leaderboard.sort(key=lambda x: (x['win_rate'], x['quality_avg']), reverse=True)
        
        return leaderboard

    def should_promote_challenger(self) -> Optional[str]:
        """
        Determine if any challenger should become the new champion
        
        Returns:
            Model ID of new champion, or None if current champion holds
        """
        leaderboard = self.get_arena_leaderboard()
        
        if len(leaderboard) < 2:
            return None
            
        current_champion = None
        best_challenger = None
        
        for model in leaderboard:
            if model['status'] == 'champion':
                current_champion = model
            elif best_challenger is None:
                best_challenger = model
        
        if not current_champion or not best_challenger:
            return None
            
        # Promotion criteria: challenger needs significantly better performance
        win_rate_advantage = best_challenger['win_rate'] - current_champion['win_rate']
        quality_advantage = best_challenger['quality_avg'] - current_champion['quality_avg']
        
        # Challenger needs at least 10% better win rate OR 0.1 better quality average
        if win_rate_advantage >= 0.1 or quality_advantage >= 0.1:
            if best_challenger['total_insights'] >= 10:  # Minimum battle experience
                return best_challenger['model_id']
        
        return None

    def promote_new_champion(self, new_champion_id: str):
        """Promote a new champion and demote the current one"""
        # Demote current champion
        for model_id, model in self.clients.models.items():
            if model['status'] == 'champion':
                model['status'] = 'challenger'
                print(f"👑➡️🥈 {model['name']} demoted to challenger")
        
        # Promote new champion
        self.clients.models[new_champion_id]['status'] = 'champion'
        champion_name = self.clients.models[new_champion_id]['name']
        print(f"🥈➡️👑 {champion_name} promoted to CHAMPION!")
        
        self.save_arena_data()

# Arena instance for use by other modules
arena = ModelArena()

async def run_competitive_insight_generation(domain: str, content: str) -> Dict:
    """
    Main function to generate insights using competitive model system
    
    Args:
        domain: Domain to analyze
        content: Content to analyze
        
    Returns:
        Winning insight data
    """
    # Run arena battle
    battle_result = await arena.battle_round(domain, content)
    
    # Check if champion should be dethroned
    new_champion = arena.should_promote_challenger()
    if new_champion:
        arena.promote_new_champion(new_champion)
    
    return battle_result['winner_insight']

def get_current_champion() -> str:
    """Get the current champion model ID"""
    for model_id, model in arena.clients.models.items():
        if model['status'] == 'champion':
            return model_id
    
    return 'deepseek-r1'  # Default fallback

def get_arena_status() -> Dict:
    """Get current arena status for monitoring"""
    leaderboard = arena.get_arena_leaderboard()
    
    return {
        'leaderboard': leaderboard,
        'current_champion': get_current_champion(),
        'total_battles': sum(m['battle_wins'] + m['battle_losses'] 
                           for m in arena.clients.models.values()),
        'arena_active': True
    }

if __name__ == "__main__":
    # Test the arena system
    import asyncio
    
    async def test_arena():
        # Test battle with sample domain
        result = await run_competitive_insight_generation(
            "stripe.com",
            "Stripe is a technology company that builds economic infrastructure for the internet."
        )
        
        print(f"\nWinner: {result['model_name']}")
        print(f"Quality: {result['quality_score']:.3f}")
        print(f"Content: {result['content'][:100]}...")
        
        # Show leaderboard
        status = get_arena_status()
        print(f"\n🏆 ARENA LEADERBOARD:")
        for i, model in enumerate(status['leaderboard'], 1):
            status_icon = "👑" if model['status'] == 'champion' else "🥊"
            print(f"{i}. {status_icon} {model['name']} - "
                  f"Win Rate: {model['win_rate']:.1%}, "
                  f"Quality: {model['quality_avg']:.3f}")
    
    # Run test
    asyncio.run(test_arena())