# Azure Setup Guide for OpsMind AI

This guide walks through configuring Microsoft Foundry IQ for OpsMind AI.

## Prerequisites

- Azure subscription. A free trial works for hackathon testing.
- Azure CLI installed.
- Python 3.11 or newer.
- OpsMind AI repository cloned locally.

## Step 1: Create Azure AI Foundry Hub and Project

1. Go to https://ai.azure.com.
2. Create a new Hub, or use an existing Hub.
3. Create a new Project inside the Hub.
4. Open the Project Overview page.
5. Copy the Project connection string.
6. Save it in `.env`:

```bash
AZURE_AI_PROJECT_CONNECTION_STRING=<your-project-connection-string>
```

## Step 2: Create Azure AI Search Resource

1. Go to Azure Portal > Create resource > Azure AI Search.
2. Choose the Free tier (F0) for testing.
3. Note that Free tier has limits, including one index.
4. Copy the Search endpoint URL from the resource Overview page.
5. Copy an Admin key from the Keys page.
6. Link the Search resource to your Azure AI Foundry Hub.

Save the Search endpoint for REST fallback:

```bash
FOUNDRY_IQ_ENDPOINT=https://<your-search-resource>.search.windows.net
```

## Step 3: Create Foundry IQ Knowledge Base

1. In Azure AI Foundry portal, open your Project.
2. Go to Agents > Knowledge Bases.
3. Create a new Knowledge Base.
4. Select your Azure AI Search resource.
5. Upload the markdown files from `knowledge_base/runbooks/`.
6. Wait for indexing to complete.
7. Copy the Knowledge Base ID.
8. Save it in `.env`:

```bash
FOUNDRY_IQ_KNOWLEDGE_BASE_ID=<your-knowledge-base-id>
```

## Step 4: Set Authentication

### Option A: DefaultAzureCredential

This is recommended for local development and demos.

1. Sign in with Azure CLI:

```bash
az login
```

2. Set authentication mode:

```bash
FOUNDRY_IQ_AUTH_MODE=credential
```

### Option B: API Key

Use this when role-based authentication is not available.

1. Copy the Admin key from your Azure AI Search resource.
2. Save it in `.env`:

```bash
FOUNDRY_IQ_API_KEY=<your-key>
FOUNDRY_IQ_AUTH_MODE=apikey
```

## Step 5: Enable Foundry Retrieval Mode

Update `.env`:

```bash
OPSMIND_RETRIEVAL_MODE=foundry
```

## Step 6: Test the Connection

Run:

```bash
python -m app.opsmind.cli "Linux VM CPU spike" --severity sev2 --environment production
```

Expected result: OpsMind returns a structured troubleshooting response citing Foundry IQ knowledge base documents.

## Cost Estimate

- Azure AI Search Free tier: $0/month, with limited features.
- Azure AI Search Basic tier: approximately $75/month.
- Foundry IQ agentic retrieval: priced per query. Check current pricing at https://azure.microsoft.com/en-us/pricing/details/microsoft-foundry/.
- For hackathon testing: Free tier plus minimal queries should be near $0 cost.

## Troubleshooting

### ClientAuthenticationError

You are not authenticated or you are signed in to the wrong tenant.

Fix:

```bash
az login
```

Then confirm the account has access to the Foundry project and Search resource.

### ResourceNotFound

The knowledge base ID is wrong or the knowledge base is not available in the selected project.

Fix:

- Recopy `FOUNDRY_IQ_KNOWLEDGE_BASE_ID`.
- Confirm the knowledge base exists in Azure AI Foundry.
- Confirm your project connection string points to the expected project.

### HttpResponseError 401

The API key is wrong or expired.

Fix:

- Copy the Admin key again from Azure AI Search.
- Update `FOUNDRY_IQ_API_KEY`.
- Confirm `FOUNDRY_IQ_AUTH_MODE=apikey` if using API key auth.

### No Results Returned

The knowledge base might not be indexed yet, or the documents do not match the query.

Fix:

- Wait a few minutes after upload.
- Confirm indexing completed successfully.
- Test with a query that matches a runbook title, such as `Linux VM CPU spike`.
- Verify the runbook markdown files were uploaded.
