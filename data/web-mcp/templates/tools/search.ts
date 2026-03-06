/**
 * Search Tool - Esempio di tool per ricerca prodotti
 * 
 * Questo tool dimostra come implementare una ricerca con parametri
 * e restituzione di risultati strutturati.
 */

import { createTool, WebMCPContext } from '@/lib/webmcp';

export interface SearchProductsParams {
  /** Query di ricerca */
  query: string;
  /** Categoria prodotto (opzionale) */
  category?: string;
  /** Prezzo minimo */
  minPrice?: number;
  /** Prezzo massimo */
  maxPrice?: number;
  /** Ordinamento: 'relevance' | 'price_asc' | 'price_desc' | 'newest' */
  sortBy?: 'relevance' | 'price_asc' | 'price_desc' | 'newest';
  /** Numero massimo di risultati */
  limit?: number;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  imageUrl?: string;
  inStock: boolean;
  rating: number;
}

export interface SearchProductsResult {
  success: boolean;
  products: Product[];
  totalCount: number;
  query: string;
  error?: string;
}

/**
 * Mock database di prodotti per l'esempio
 */
const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Laptop Pro X1',
    description: 'Laptop professionale ad alte prestazioni',
    price: 1299.99,
    category: 'electronics',
    imageUrl: '/images/laptop.jpg',
    inStock: true,
    rating: 4.5
  },
  {
    id: '2',
    name: 'Smartphone Ultra',
    description: 'Smartphone con fotocamera professionale',
    price: 899.99,
    category: 'electronics',
    imageUrl: '/images/phone.jpg',
    inStock: true,
    rating: 4.7
  },
  {
    id: '3',
    name: 'Cuffie Wireless',
    description: 'Cuffie con cancellazione attiva del rumore',
    price: 249.99,
    category: 'electronics',
    imageUrl: '/images/headphones.jpg',
    inStock: true,
    rating: 4.3
  },
  {
    id: '4',
    name: 'T-Shirt Premium',
    description: 'T-shirt in cotone organico',
    price: 29.99,
    category: 'clothing',
    imageUrl: '/images/tshirt.jpg',
    inStock: true,
    rating: 4.0
  },
  {
    id: '5',
    name: 'Jeans Slim Fit',
    description: 'Jeans slim fit in denim premium',
    price: 79.99,
    category: 'clothing',
    imageUrl: '/images/jeans.jpg',
    inStock: false,
    rating: 4.2
  }
];

/**
 * Tool per la ricerca di prodotti
 */
export const searchProductsTool = createTool<
  SearchProductsParams,
  SearchProductsResult
>({
  name: 'searchProducts',
  description: 'Cerca prodotti nel catalogo con filtri per categoria, prezzo e ordinamento',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Termine di ricerca per nome o descrizione prodotto'
      },
      category: {
        type: 'string',
        description: 'Filtra per categoria (electronics, clothing, ecc.)'
      },
      minPrice: {
        type: 'number',
        description: 'Prezzo minimo'
      },
      maxPrice: {
        type: 'number',
        description: 'Prezzo massimo'
      },
      sortBy: {
        type: 'string',
        enum: ['relevance', 'price_asc', 'price_desc', 'newest'],
        description: 'Criterio di ordinamento'
      },
      limit: {
        type: 'number',
        description: 'Numero massimo di risultati (default: 10)'
      }
    },
    required: ['query']
  },
  
  async execute(
    params: SearchProductsParams,
    context: WebMCPContext
  ): Promise<SearchProductsResult> {
    try {
      console.log('[searchProducts] Ricerca con parametri:', params);
      console.log('[searchProducts] Context:', context);
      
      const {
        query,
        category,
        minPrice,
        maxPrice,
        sortBy = 'relevance',
        limit = 10
      } = params;
      
      // Filtra i prodotti
      let results = mockProducts.filter(product => {
        // Filtro per query (nome o descrizione)
        const matchesQuery = 
          product.name.toLowerCase().includes(query.toLowerCase()) ||
          product.description.toLowerCase().includes(query.toLowerCase());
        
        // Filtro per categoria
        const matchesCategory = !category || product.category === category;
        
        // Filtro per prezzo minimo
        const matchesMinPrice = minPrice === undefined || product.price >= minPrice;
        
        // Filtro per prezzo massimo
        const matchesMaxPrice = maxPrice === undefined || product.price <= maxPrice;
        
        return matchesQuery && matchesCategory && matchesMinPrice && matchesMaxPrice;
      });
      
      // Ordina i risultati
      switch (sortBy) {
        case 'price_asc':
          results.sort((a, b) => a.price - b.price);
          break;
        case 'price_desc':
          results.sort((a, b) => b.price - a.price);
          break;
        case 'newest':
          // In un caso reale, ordinare per data
          results.reverse();
          break;
        case 'relevance':
        default:
          // Ordina per rilevanza (rating in questo esempio)
          results.sort((a, b) => b.rating - a.rating);
          break;
      }
      
      // Limita i risultati
      const limitedResults = results.slice(0, limit);
      
      return {
        success: true,
        products: limitedResults,
        totalCount: results.length,
        query
      };
    } catch (error) {
      console.error('[searchProducts] Errore:', error);
      
      return {
        success: false,
        products: [],
        totalCount: 0,
        query: params.query,
        error: error instanceof Error ? error.message : 'Errore sconosciuto'
      };
    }
  }
});

export default searchProductsTool;
