type Attachment = {
	filename: string;
	content: string;
};

type Summary = {
	file: string;
	text: string;
};

export interface Log {
	id: number;
	subject: string;
	sender: string;
	body: string;
	attachments?: Attachment[];
	summary: Summary[];
	processed: boolean;
	received_at: string;
}
