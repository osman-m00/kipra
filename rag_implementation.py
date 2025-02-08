import os
from typing import List, Dict
import numpy as np
from deepseek import DeepSeek
import faiss
from scrape_blogs import scrape_all_blogs
from scrape_properties import get_property_listings

class RAGChatbot:
    def __init__(self, api_key):
        self.deepseek = DeepSeek(api_key=api_key)
        self.dimension = 1536  # Deepseek embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.properties = []
        
    def initialize(self):
        # Scrape and index blog content
        blog_contents = scrape_all_blogs()
        for url, blog in blog_contents.items():
            doc = f"Title: {blog['title']}\nContent: {blog['content']}"
            self.documents.append({
                'content': doc,
                'url': url,
                'type': 'blog'
            })
        
        # Get and index property listings
        properties = get_property_listings()
        for prop in properties:
            doc = f"Property: {prop['title']}\nLocation: {prop['location']}\nPrice: {prop['price']}"
            self.documents.append({
                'content': doc,
                'url': prop['link'],
                'type': 'property'
            })
        
        # Create embeddings and build index
        embeddings = []
        for doc in self.documents:
            embedding = self.deepseek.embeddings.create(
                input=doc['content'],
                model="deepseek-embed-v1"
            )
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        
    def search_relevant_docs(self, query: str, k: int = 3) -> List[Dict]:
        query_embedding = self.deepseek.embeddings.create(
            input=query,
            model="deepseek-embed-v1"
        )
        
        query_embedding_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_embedding_array, k)
        
        relevant_docs = []
        for idx in indices[0]:
            relevant_docs.append(self.documents[idx])
        return relevant_docs
    
    def get_chat_response(self, user_input: str) -> Dict:
        # Get relevant documents
        relevant_docs = self.search_relevant_docs(user_input)
        
        # Prepare context from relevant documents
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # Check if the query is about properties
        property_keywords = ['apartment', 'house', 'rent', 'sale', 'property', 'bedroom', 'flat']
        is_property_query = any(keyword in user_input.lower() for keyword in property_keywords)
        
        if is_property_query:
            properties = get_property_listings()  # Get fresh property listings
            property_info = "\n".join([f"- {p['title']} ({p['location']}) - {p['price']}: {p['link']}" 
                                     for p in properties[:3]])
            context += f"\n\nRelevant Properties:\n{property_info}"
        
        # Prepare the prompt
        prompt = f"""You are a helpful real estate assistant for Kipra Homes. 
        Use the following context to answer the user's question:
        
        {context}
        
        User Question: {user_input}
        
        Please provide a helpful and informative response. If the question is about properties,
        include relevant property listings and their links."""
        
        # Get response from Deepseek
        response = self.deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'response': response.choices[0].message.content,
            'sources': [{'url': doc['url'], 'type': doc['type']} for doc in relevant_docs]
        } 