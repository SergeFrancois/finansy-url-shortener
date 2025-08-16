# URL shortener service
This is a simple web server that allows you to create and use short URLs similar to [Bitly](https://bitly.com).
Web server is built using [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLite](https://sqlite.org/).
## Installation and run
To run the web server simply clone the repository to a machine with Docker Compose installed (I used version 2.39.1) and enter the command:
```
docker compose up
```
If port 5001 is already occupied by another service, change the port in the [compose](./compose.yaml) file and try again.
## Usage
Documentation on using the web server can be viewed in [Swagger](http://localhost:5001/docs) or [ReDoc](http://localhost:5001/redoc) formats.
Below are several examples of how the web server can be used.
### Example 1. Create shorten URL
#### Request:
```bash
curl -H 'Content-Type: application/json' -d '{"url": "https://litnet.com"}' http://localhost:5001/api/v1/shorten
```
#### Response:
```json
{
    "shorten_url": "http://localhost:5001/s/lxenWI"
}
```
### Example 2. Redirect to original URL
#### Request:
```bash
curl -L http://192.168.56.103:5001/s/lxenWI
```
#### Response:
`Too many HTML and JS lines...`
### Example 3. Get statistics
#### Request:
```bash
curl http://localhost:5001/api/v1/stats/lxenWI
```
#### Response:
```json
{
    "code": "lxenWI",
    "original_url": "https://litnet.com/",
    "request_count": 1,
    "creation_timestamp": "2025-08-16T20:01:35.230274"
}
```