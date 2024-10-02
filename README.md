# Web Scraper for Liquidation Deals

This project is a web scraper designed to gather data from liquidation websites, process it, and provide insights into auction items and their demand. The current implementation focuses on `liquidation.com`.

## Setup Instructions

1. **Clone the repository:**

   ```sh
   git clone https://github.com/vandyand/max-liquidation.git
   cd max-liquidation
   ```

2. **Install the required Python packages:**

   ```sh
   source setup.sh
   ```

3. **Run the scraper:**
   ```sh
   ./main.sh
   ```

## API
The python api is built with FastAPI and is located in the `src/api` directory.

To run the API, use the following command:
```sh
uvicorn src.api.api:app --reload
```

## License

This project is licensed under the MIT License.
