import os
from google import genai
from google.genai import types
from typing import Dict, Any
import src.utils as utils

class Node3_Gemini:
    """
    Node 3: Responsible for generating summaries using Google's Gemini LLM.
    """
    def __init__(self) -> None:
        """Initializes the Gemini model."""
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = 'gemini-2.5-flash-lite'
        
    def generate_summary(self, structured_data: Dict[str, Any]) -> str:
        """
        Generates a markdown summary of the tweet content.

        Args:
            structured_data (Dict[str, Any]): The structured tweet data from Node 2.

        Returns:
            str: The generated summary in Markdown format.
        """
        print("Node 3: Generating summary with Gemini (Search Grounding Disabled)...")
        
        # Prepare content parts
        
        # System Prompt
        system_prompt = "You are a helpful assistant that summarizes X posts. Analyze the intent and content. Output in Markdown."
        try:
            base_path = os.path.dirname(os.path.dirname(__file__)) # Go up one level to src/
            file_path = os.path.join(base_path, "system_prompt.md")
            with open(file_path, "r") as f:
                system_prompt = f.read()
                # Replace placeholder with actual post text
                system_prompt = system_prompt.replace("{専門的なコメント}", structured_data['text'])
        except FileNotFoundError:
            pass
            
        prompt_text = system_prompt
        prompt_text += f"\n\n【対象の投稿テキスト】\n{structured_data['text']}"
        
        # Explicitly mention NOT to use external search and rely on the text
        prompt_text += "\n\n【指示】\n上記の【対象の投稿テキスト】の内容に基づいて、正確な解説を生成してください。\n外部情報の検索は行わず、提供されたテキスト情報のみを正として処理してください。\n全く無関係なトピックの生成は禁止します。\n最終的な出力は必ず日本語で行ってください。"
        
        try:
            # Generate content without tools (Web Search disabled)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    # Explicitly disable tools to prevent web search
                    tools=[]
                )
            )
            
            # Debug logs
            print(f"DEBUG: Full Gemini Response: {response}")
            if response.candidates:
                print(f"DEBUG: Candidate 0 Finish Reason: {response.candidates[0].finish_reason}")
                if response.candidates[0].content:
                     print(f"DEBUG: Candidate 0 Content: {response.candidates[0].content}")
                else:
                     print("DEBUG: Candidate 0 has no content.")
            else:
                print("DEBUG: No candidates returned.")
                
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "# Error Generating Summary\n\nCould not generate summary due to an error."
