import axios from 'axios';
import type { Log } from '../types.ts';

const API_URL = 'http://localhost:8000';

export async function fetchLogs(): Promise<Log[]> {
	const response = await axios.get(`${API_URL}/logs`, {
		headers: { accept: 'application/json' }
	});
	return response.data;
}
