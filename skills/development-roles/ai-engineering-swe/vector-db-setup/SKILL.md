---
name: vector-db-setup
description: >-
  Sets up vector databases for semantic search including Pinecone, Chroma, pgvector, and Qdrant with embedding generation and similarity search. Use when users request "vector database", "semantic search", "embeddings storage", "Pinecone setup", or "similarity search".
license: MIT
metadata:
  version: "1.0"
  category: ai-engineering-swe
---

# Vector Database Setup

Configure vector databases for semantic search and AI applications.

## Core Workflow

1. **Choose database**: Select based on requirements
2. **Setup connection**: Configure client
3. **Generate embeddings**: Create vector representations
4. **Index documents**: Store with metadata
5. **Query vectors**: Semantic similarity search
6. **Optimize**: Tune for performance

## Database Comparison

| Database | Type | Best For | Scaling |
|----------|------|----------|---------|
| Pinecone | Managed | Production, no ops | Automatic |
| Chroma | Embedded/Server | Development, local | Manual |
| pgvector | PostgreSQL ext | Existing Postgres | With Postgres |
| Qdrant | Self-hosted | Full control | Manual |
| Weaviate | Managed/Self | GraphQL-like API | Both |

## Embeddings Generation

### OpenAI Embeddings

```typescript
// embeddings/openai.ts
import OpenAI from 'openai';

const openai = new OpenAI();

export async function generateEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small', // or text-embedding-3-large
    input: text,
  });

  return response.data[0].embedding;
}

export async function generateEmbeddings(texts: string[]): Promise<number[][]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: texts,
  });

  return response.data.map((d) => d.embedding);
}
```

### Batch Processing

```typescript
// embeddings/batch.ts
const BATCH_SIZE = 100;

export async function batchGenerateEmbeddings(
  texts: string[]
): Promise<number[][]> {
  const embeddings: number[][] = [];

  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const batch = texts.slice(i, i + BATCH_SIZE);
    const batchEmbeddings = await generateEmbeddings(batch);
    embeddings.push(...batchEmbeddings);

    // Rate limiting
    if (i + BATCH_SIZE < texts.length) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  return embeddings;
}
```

## Best Practices

1. **Choose the right dimension**: Match embedding model
2. **Use namespaces**: Organize data logically
3. **Add metadata**: Enable filtering
4. **Batch operations**: Reduce API calls
5. **Index appropriately**: HNSW for speed, IVF for memory
6. **Monitor performance**: Track latency and recall
7. **Cache embeddings**: Avoid regenerating
8. **Use hybrid search**: Combine vector and keyword

## Output Checklist

Every vector database setup should include:

- [ ] Database client configured
- [ ] Embedding generation function
- [ ] Collection/index creation
- [ ] Document upsert with metadata
- [ ] Similarity search function
- [ ] Filtered search capability
- [ ] Batch processing for large datasets
- [ ] Delete/update operations
- [ ] Error handling
- [ ] Performance monitoring


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

