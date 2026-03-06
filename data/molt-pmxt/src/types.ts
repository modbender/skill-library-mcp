export interface Market {
    id: string;
    exchange: string;
    title: string;
    description: string;
    volume: number;
    resolved: boolean;
}

export interface Token {
    id: string;
    symbol: string;
    price: number;
}

export interface OrderbookSnapshot {
    market_id: string;
    bids: Order[];
    asks: Order[];
    timestamp: string;
}

export interface Order {
    price: number;
    size: number;
}

export interface ToolResult<T> {
    success: boolean;
    data?: T;
    error?: string;
}
