# Local API Testing

This folder contains resources for testing the API endpoints locally.

## `requests.http`

This file provides a convenient way to send requests to the running API using the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension for Visual Studio Code.

### Prerequisites

-   [Visual Studio Code](https://code.visualstudio.com/)
-   [REST Client Extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) installed in VS Code.

### How to Use

1.  **Start the API server** by running the following command from the `Deployment` directory:
    ```bash
    uvicorn src.main:app --reload
    ```

2.  **Open the `requests.http` file** in VS Code.

3.  You will see a "Send Request" link appear above each `POST` or `GET` request definition.

4.  **Click "Send Request"** for the endpoint you wish to test.

5.  A new editor pane will open to the side, displaying the response from the API.

### File Structure

-   **Variables**: At the top of the file, variables like `@baseUrl` are defined. You can change the port here if you run the server on a different one.
-   **Requests**: Each API endpoint has its own request block, separated by `###`. Each block includes the HTTP method, URL, headers, and a sample JSON body.

This setup allows for quick and easy testing of all API endpoints without leaving your code editor.
