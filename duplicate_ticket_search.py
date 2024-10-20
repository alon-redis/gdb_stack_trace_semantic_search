import openai
import argparse
import redis
import numpy as np
import os
import sys
from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# Define color and style codes
CYAN = '\033[36m'  # Cyan color
GREEN = '\033[32m'  # Green color
RED = '\033[31;40m'  # Red color
RESET = '\033[0m'  # Reset to default terminal color

def get_embeddings(text, model="text-embedding-3-small"):
    try:
        response = openai.Embedding.create(input=text, model=model, dimensions=512)
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def read_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except Exception as e:
        print(f"Failed to read the file: {str(e)}")
        return None

def connect_to_redis(host, port, password):
    try:
        return redis.Redis(host=host, port=port, password=password, decode_responses=True)
    except Exception as e:
        print(f"Failed to connect to Redis: {str(e)}")
        return None

def pretty_print_results(results, file_name):
    print(f"The nearest similar results for {CYAN}{file_name}{RESET}:")
    total_results = results[0]  # The total number of results, not used in output directly
    i = 1  # Start index after the total count
    while i < len(results):
        ticket_id = results[i]
        distance_info = results[i + 1]  # The list containing the distance and ticket ID
        distance = distance_info[1]  # The distance value is the second item in the list
        jira_id = ticket_id.split(':')[1]  # Extract the ID from 'ticket:ID' format
#        jira_id = jira_id[:3].upper() + '-' + jira_id[3:]
        print(f"{GREEN}Ticket ID: {jira_id}{RESET} - Distance: {CYAN}{distance}{RESET} - https://redislabs.atlassian.net/browse/{jira_id}")
        i += 2  # Move the index by 2 to the next ticket ID
    print(f"{RED}Results with distance > 0.03 shouldn't be considered as duplicates{RESET}")

def create_vector_index(redis_client, index_name):
    try:
        redis_client.execute_command("FT.CREATE", index_name, "ON", "HASH", "PREFIX", "1", "ticket:", "SCHEMA", "ticket", "TEXT", "SORTABLE", "embedding", "VECTOR", "FLAT", "6", "TYPE", "FLOAT32", "DIM", "512", "DISTANCE_METRIC", "COSINE")
        print("Vector index created successfully.")
    except Exception as e:
        print(f"Failed to create vector index: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate text embeddings from a specified file and store in Redis")
    parser.add_argument("file_path", type=str, help="Path to the text file from which to read text")
    parser.add_argument("--init", action="store_true", help="Flush the Redis database and create vector index")
    parser.add_argument("--query_only", action="store_false", help="Query for similar search w/o store the data")
    parser.add_argument("--KNN", type=int, default=1, help="Set the KNN value for the FT.SEARCH command")
    args = parser.parse_args()

    openai.api_key = 'OPENAI API KEY'

    # Read text from file
    file_text = read_text_from_file(args.file_path)
    if file_text is not None:
        # Get embeddings
        embeddings = get_embeddings(file_text)
#        print(embeddings)
        index_name = "idx:coredumps"
        if embeddings:
            # Connect to Redis
            redis_host = "REDIS_HOST"
            redis_port = REDIS_PORT
            redis_password = "REDIS_PASSWORD"
            redis_client = connect_to_redis(redis_host, redis_port, redis_password)
            if redis_client:
                if args.init:
                    redis_client.flushdb()
                    print("Redis database flushed successfully.")
                    # Create a new vector index for storing embeddings
                    create_vector_index(redis_client, index_name)
                    exit()
                # Extract file name from file_path to use as the hash field
                file_name = os.path.splitext(os.path.basename(args.file_path))[0]
                # Use the file name as the hash field
                embed_key = f"ticket:{file_name}"
                # convert the embeddings data to blob (Binary Large Objects) format
                blob = np.array(embeddings).astype(dtype=np.float32).tobytes()
                # perform similarity search of the embeddings in the VS DB
                results = redis_client.execute_command("FT.SEARCH", index_name, f"(*)=>[KNN {args.KNN} @embedding $input_vector AS distance]", "PARAMS", "2", "input_vector", blob, "RETURN", "2", "ticket", "distance", "SORTBY", "distance", "ASC", "DIALECT", "2")
                pretty_print_results(results, file_name)
                if args.query_only:
                    # store the new ticket info in the DB as hash
                    redis_client.execute_command("HSET", embed_key, "ticket", file_name, "embedding", blob)
                    print(f"Embeddings stored successfully in Redis under key {embed_key}.")
        else:
            print("Failed to generate embeddings.")
    else:
        print("No text to process.")
