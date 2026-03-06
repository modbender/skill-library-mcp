/**
 * Cart Tool - Esempio di tool per gestione carrello
 * 
 * Questo tool dimostra come implementare operazioni CRUD
 * su un carrello e-commerce.
 */

import { createTool, WebMCPContext } from '@/lib/webmcp';

export interface CartItem {
  productId: string;
  name: string;
  price: number;
  quantity: number;
  imageUrl?: string;
}

export interface Cart {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
}

// Stato del carrello (in memoria per l'esempio)
let cartState: Cart = {
  items: [],
  totalItems: 0,
  totalPrice: 0
};

// ============================================================================
// Add to Cart
// ============================================================================

export interface AddToCartParams {
  productId: string;
  name: string;
  price: number;
  quantity?: number;
  imageUrl?: string;
}

export interface AddToCartResult {
  success: boolean;
  cart: Cart;
  addedItem: CartItem;
  message?: string;
  error?: string;
}

export const addToCartTool = createTool<AddToCartParams, AddToCartResult>({
  name: 'addToCart',
  description: 'Aggiunge un prodotto al carrello',
  parameters: {
    type: 'object',
    properties: {
      productId: {
        type: 'string',
        description: 'ID univoco del prodotto'
      },
      name: {
        type: 'string',
        description: 'Nome del prodotto'
      },
      price: {
        type: 'number',
        description: 'Prezzo unitario'
      },
      quantity: {
        type: 'number',
        description: 'Quantità da aggiungere (default: 1)'
      },
      imageUrl: {
        type: 'string',
        description: 'URL immagine prodotto'
      }
    },
    required: ['productId', 'name', 'price']
  },
  
  async execute(
    params: AddToCartParams,
    context: WebMCPContext
  ): Promise<AddToCartResult> {
    try {
      const { productId, name, price, quantity = 1, imageUrl } = params;
      
      // Verifica se il prodotto è già nel carrello
      const existingItem = cartState.items.find(item => item.productId === productId);
      
      if (existingItem) {
        // Aggiorna quantità
        existingItem.quantity += quantity;
      } else {
        // Aggiungi nuovo item
        cartState.items.push({
          productId,
          name,
          price,
          quantity,
          imageUrl
        });
      }
      
      // Ricalcola totali
      updateCartTotals();
      
      const addedItem = cartState.items.find(item => item.productId === productId)!;
      
      console.log('[addToCart] Carrello aggiornato:', cartState);
      
      return {
        success: true,
        cart: { ...cartState },
        addedItem,
        message: `${name} aggiunto al carrello`
      };
    } catch (error) {
      return {
        success: false,
        cart: { ...cartState },
        addedItem: null as any,
        error: error instanceof Error ? error.message : 'Errore nell\'aggiunta al carrello'
      };
    }
  }
});

// ============================================================================
// Remove from Cart
// ============================================================================

export interface RemoveFromCartParams {
  productId: string;
}

export interface RemoveFromCartResult {
  success: boolean;
  cart: Cart;
  removedItem?: CartItem;
  message?: string;
  error?: string;
}

export const removeFromCartTool = createTool<RemoveFromCartParams, RemoveFromCartResult>({
  name: 'removeFromCart',
  description: 'Rimuove un prodotto dal carrello',
  parameters: {
    type: 'object',
    properties: {
      productId: {
        type: 'string',
        description: 'ID del prodotto da rimuovere'
      }
    },
    required: ['productId']
  },
  
  async execute(
    params: RemoveFromCartParams,
    context: WebMCPContext
  ): Promise<RemoveFromCartResult> {
    try {
      const { productId } = params;
      
      const itemIndex = cartState.items.findIndex(item => item.productId === productId);
      
      if (itemIndex === -1) {
        return {
          success: false,
          cart: { ...cartState },
          error: 'Prodotto non trovato nel carrello'
        };
      }
      
      const removedItem = cartState.items[itemIndex];
      cartState.items.splice(itemIndex, 1);
      
      updateCartTotals();
      
      return {
        success: true,
        cart: { ...cartState },
        removedItem,
        message: `${removedItem.name} rimosso dal carrello`
      };
    } catch (error) {
      return {
        success: false,
        cart: { ...cartState },
        error: error instanceof Error ? error.message : 'Errore nella rimozione'
      };
    }
  }
});

// ============================================================================
// Update Cart Item Quantity
// ============================================================================

export interface UpdateCartItemParams {
  productId: string;
  quantity: number;
}

export interface UpdateCartItemResult {
  success: boolean;
  cart: Cart;
  updatedItem?: CartItem;
  message?: string;
  error?: string;
}

export const updateCartItemTool = createTool<UpdateCartItemParams, UpdateCartItemResult>({
  name: 'updateCartItem',
  description: 'Aggiorna la quantità di un prodotto nel carrello',
  parameters: {
    type: 'object',
    properties: {
      productId: {
        type: 'string',
        description: 'ID del prodotto'
      },
      quantity: {
        type: 'number',
        description: 'Nuova quantità (0 per rimuovere)'
      }
    },
    required: ['productId', 'quantity']
  },
  
  async execute(
    params: UpdateCartItemParams,
    context: WebMCPContext
  ): Promise<UpdateCartItemResult> {
    try {
      const { productId, quantity } = params;
      
      if (quantity <= 0) {
        // Rimuovi se quantità è 0 o negativa
        return removeFromCartTool.execute({ productId }, context);
      }
      
      const item = cartState.items.find(item => item.productId === productId);
      
      if (!item) {
        return {
          success: false,
          cart: { ...cartState },
          error: 'Prodotto non trovato nel carrello'
        };
      }
      
      item.quantity = quantity;
      updateCartTotals();
      
      return {
        success: true,
        cart: { ...cartState },
        updatedItem: item,
        message: `Quantità di ${item.name} aggiornata a ${quantity}`
      };
    } catch (error) {
      return {
        success: false,
        cart: { ...cartState },
        error: error instanceof Error ? error.message : 'Errore nell\'aggiornamento'
      };
    }
  }
});

// ============================================================================
// Get Cart
// ============================================================================

export interface GetCartParams {
  // Nessun parametro richiesto
}

export interface GetCartResult {
  success: boolean;
  cart: Cart;
  error?: string;
}

export const getCartTool = createTool<GetCartParams, GetCartResult>({
  name: 'getCart',
  description: 'Recupera il contenuto attuale del carrello',
  parameters: {
    type: 'object',
    properties: {}
  },
  
  async execute(
    params: GetCartParams,
    context: WebMCPContext
  ): Promise<GetCartResult> {
    return {
      success: true,
      cart: { ...cartState }
    };
  }
});

// ============================================================================
// Clear Cart
// ============================================================================

export interface ClearCartParams {
  // Nessun parametro richiesto
}

export interface ClearCartResult {
  success: boolean;
  message: string;
  error?: string;
}

export const clearCartTool = createTool<ClearCartParams, ClearCartResult>({
  name: 'clearCart',
  description: 'Svuota completamente il carrello',
  parameters: {
    type: 'object',
    properties: {}
  },
  
  async execute(
    params: ClearCartParams,
    context: WebMCPContext
  ): Promise<ClearCartResult> {
    cartState = {
      items: [],
      totalItems: 0,
      totalPrice: 0
    };
    
    return {
      success: true,
      message: 'Carrello svuotato'
    };
  }
});

// ============================================================================
// Helper Functions
// ============================================================================

function updateCartTotals(): void {
  cartState.totalItems = cartState.items.reduce((sum, item) => sum + item.quantity, 0);
  cartState.totalPrice = cartState.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
}

// Esporta tutti i tool del carrello
export const cartTools = [
  addToCartTool,
  removeFromCartTool,
  updateCartItemTool,
  getCartTool,
  clearCartTool
];

export default cartTools;
