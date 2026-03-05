import asyncio
import aiofiles
import os
import json
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from aiohttp import FormData

async def load_tokens(file_path: str) -> List[str]:
    """
    Load tokens from a file.
    
    Args:
        file_path (str): Path to the file containing tokens
        
    Returns:
        List[str]: List of tokens
    """
    tokens = []
    try:
        async with aiofiles.open(file_path, mode='r', encoding="latin-1") as f:
            async for line in f:
                line = line.strip()
                if line:
                    tokens.append(line)
        return tokens
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return []

async def save_results(file_path: str, data: Union[str, List[str]]) -> bool:
    """
    Save results to a file.
    
    Args:
        file_path (str): Path to the file to save results
        data (Union[str, List[str]]): Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, mode='w', encoding="utf-8") as f:
            if isinstance(data, list):
                await f.write('\n'.join(data))
            else:
                await f.write(data)
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

async def read_image_as_base64(file_path: str) -> Optional[str]:
    """
    Read an image file and convert it to base64.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        Optional[str]: Base64-encoded image data or None if failed
    """
    try:
        async with aiofiles.open(file_path, mode='rb') as f:
            image_data = await f.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def create_form_data(data: Dict[str, Any]) -> FormData:
    """
    Create FormData from a dictionary.
    
    Args:
        data (Dict[str, Any]): Dictionary of form data
        
    Returns:
        FormData: FormData object
    """
    form = FormData()
    for key, value in data.items():
        if value is not None:
            form.add_field(key, str(value))
    return form

def create_graphql_payload(variables: Dict[str, Any], features: Dict[str, bool], query_id: str) -> Dict[str, Any]:
    """
    Create a GraphQL payload.
    
    Args:
        variables (Dict[str, Any]): GraphQL variables
        features (Dict[str, bool]): GraphQL features
        query_id (str): GraphQL query ID
        
    Returns:
        Dict[str, Any]: GraphQL payload
    """
    return {
        "variables": variables,
        "features": features,
        "queryId": query_id
    }

def parse_user_id_from_response(response: Dict[str, Any]) -> Optional[str]:
    """
    Parse user ID from a response.
    
    Args:
        response (Dict[str, Any]): Response from Twitter API
        
    Returns:
        Optional[str]: User ID or None if not found
    """
    try:
        if 'data' in response and 'user' in response['data'] and 'result' in response['data']['user']:
            return response['data']['user']['result']['rest_id']
        elif 'id_str' in response:
            return response['id_str']
        return None
    except Exception as e:
        print(f"Error parsing user ID: {e}")
        return None

def format_error_message(error: Exception) -> str:
    """
    Format an error message.
    
    Args:
        error (Exception): Exception object
        
    Returns:
        str: Formatted error message
    """
    return f"{type(error).__name__}: {str(error)}"

async def run_concurrent_tasks(tasks: List[asyncio.Task], max_concurrent: int = 10) -> List[Any]:
    """
    Run tasks concurrently with a limit on the number of concurrent tasks.
    
    Args:
        tasks (List[asyncio.Task]): List of tasks to run
        max_concurrent (int, optional): Maximum number of concurrent tasks. Defaults to 10.
        
    Returns:
        List[Any]: List of results
    """
    results = []
    for i in range(0, len(tasks), max_concurrent):
        batch = tasks[i:i + max_concurrent]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        results.extend(batch_results)
    return results 