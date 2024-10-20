# GDB stack trace similarity search using Redis VS and openai embeddings

This Python script uses the OpenAI API to generate embeddings from text files and stores these embeddings in a Redis database using RediSearch's vector indexing capabilities.

### Prerequisites
- Python 3.6+
- OpenAI API key
- Redis instance with RediSearch installed and configured
- Required Python libraries: `redis-py`, `numpy`, `openai`

### Installation
1. **Install Python Dependencies**
   ```bash
   pip install openai redis numpy
   ```

2. **Setup Redis**
   - Ensure your Redis instance has RediSearch installed.
   - The Redis server should be accessible with the given host, port, and password.

3. **Configure API Key**
   - Set your OpenAI API key in the script or as an environment variable for enhanced security.

### Usage
1. **Running the Script**
   - The script is executed from the command line with the path to the text file from which you want to generate embeddings.
   ```bash
   python embeddings_redis.py <path_to_text_file>
   ```

2. **Command Line Options**
   - `--flush`: Flush the Redis database on startup.
   - `--create_index`: Create the vector index if specified. Useful if running for the first time or if the index has been deleted.
   - `--KNN`: Specify the number of nearest neighbors to retrieve in the search. Default is 1.

### Features
- **Embedding Generation**: Converts text from files into 512-dimensional embeddings using OpenAI's API.
- **Redis Storage**: Stores and retrieves embeddings using vector fields in Redis, allowing for efficient similarity searches.
- **Enhanced Output**: Results from similarity searches are displayed in a user-friendly manner, highlighting key information.

### Configuration
- Modify the Redis connection settings (`redis_host`, `redis_port`, `redis_password`) as per your environment.
- Update the OpenAI API key in the script.

### Example
```bash
python embeddings_redis.py sample.txt --create_index --flush --KNN 3
```
This command will read text from `sample.txt`, flush the database, create a vector index, generate embeddings, store them in Redis, and perform a KNN search with 5 nearest neighbors.

### Troubleshooting
- **API Key Errors**: Ensure the API key is correctly set and has the necessary permissions.
- **Redis Connection Issues**: Check the connectivity details and ensure Redis is running with the required modules.
- **File Not Found**: Verify the file path is correct and accessible.

### gdb stuck trace format
```
#0  __GI_raise (sig=sig@entry=6) at ../sysdeps/unix/sysv/linux/raise.c:51
#1  0x00007f76a0f938cb in __GI_abort () at abort.c:100
#2  0x00007f76a0f833fa in __assert_fail_base (fmt=0x7f76a110a6c0 "%s%s%s:%u: %s%sAssertion `%s' failed.\n%n", assertion=assertion@entry=0x561c4d73522f "ident",
    file=file@entry=0x561c4d707010 "/garantia.cluster/dmcproxy/dmc/bdb/identity.cpp", line=line@entry=320,
    function=function@entry=0x561c4d707300 <dmc_bdb_identity_setuser_fault_record::__PRETTY_FUNCTION__> "void dmc_bdb_identity_setuser_fault_record(bdb_identity_t*)") at assert.c:92
#3  0x00007f76a0f83472 in __GI___assert_fail (assertion=assertion@entry=0x561c4d73522f "ident", file=file@entry=0x561c4d707010 "/garantia.cluster/dmcproxy/dmc/bdb/identity.cpp", line=line@entry=320,
    function=function@entry=0x561c4d707300 <dmc_bdb_identity_setuser_fault_record::__PRETTY_FUNCTION__> "void dmc_bdb_identity_setuser_fault_record(bdb_identity_t*)") at assert.c:101
#4  0x0000561c4d14219a in dmc_bdb_identity_setuser_fault_record (ident=ident@entry=0x0) at /garantia.cluster/dmcproxy/dmc/bdb/identity.cpp:320
#5  0x0000561c4d1f46f1 in dmc_sconn_bdb_setuser_on_response (sconn=0x7f76755c1b50, identity=0x0, response=response@entry=0x7f768be7c530 "-ERR Protocol error: expected '$', got ' '\r\n\034V", len=len@entry=44)
    at /garantia.cluster/dmcproxy/dmc/net/server_connection.c:428
```

