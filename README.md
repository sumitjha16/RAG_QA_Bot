# 💬 PDF QA Assistant

## Overview
PDF QA Assistant is an interactive Streamlit app that allows users to upload PDF documents, generate summaries, and ask questions about the content of the PDF files using an integrated backend. The app also supports exporting chat conversations and summaries as downloadable files.

## Demo



![image](https://github.com/user-attachments/assets/af04b635-ec6d-4d52-9c00-dcb2244caa89)

![image](https://github.com/user-attachments/assets/9d32314a-e371-4fe3-9252-996ed3a41ba5)

![image](https://github.com/user-attachments/assets/ca6d3caa-0658-444e-a91d-eac5dc750a6d)



## Features
- **Upload PDF Documents**: Upload a PDF file to summarize and analyze.
- **Generate Summaries**: Automatically generate a summary of the uploaded PDF.
- **Ask Questions**: Ask questions related to the content of the PDF document.
- **Export Conversations**: Export conversations as PDF or text.
- **New Sessions**: Reset the conversation and upload a new PDF document.

## Prerequisites
- **Python 3.7 or higher**
- **Docker (optional)**: For easy containerized deployment.
- **Streamlit**: For building and running the front-end.

## Local Installation and Setup

## Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/pdf-qa-assistant.git
cd pdf-qa-assistant
 ```


## Step 2: Local Deployement

> Note: The first time you run this, it might take a while to build all the images and download the embedding models.

1. You will need an API key from Cohere Api. You can create one for free here:
    - [Cohere Api ](https://cohere.com) - to use models like Cohere (Recommended since it's free)
    - [OpenIA](https://platform.openai.com/account/api-keys) - to use models like GPT4
2. Set up your API keys in a file called `.env` (see `.env.example` for an example)

3. Now set up the backend and frontend

    ```shell
    docker compose up
    ```

    Or if in case you don't have docker or facing any issue then you can run backend and frontend individually like this
   ![image](https://github.com/user-attachments/assets/ab7726d8-1506-4d7b-a35f-4bc213ebcd16)

5. Navigate to the frontend in your browser: [http://localhost:8501/](http://localhost:8501/)
6. Upload a PDF document that you would like to ask a question,or sumaarize about
7. Ask a question in the chat input section and wait for a response




