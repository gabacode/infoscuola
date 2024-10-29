export interface Log {
	id: number;
	subject: string;
	sender: string;
	body: string;
	attachments?: Record<string, any>[];
	summary?: Record<string, any>[];
	processed: boolean;
	received_at: string;
}
