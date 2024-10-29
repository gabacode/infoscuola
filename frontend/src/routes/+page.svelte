<script lang="ts">
	import { onMount } from 'svelte';
	import type { Log } from '../types.js';
	import { fetchLogs } from '$lib/api.js';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	let logs: Log[] = [];
	let error: string | null = null;

	onMount(async () => {
		try {
			logs = await fetchLogs();
		} catch (e) {
			error = 'Failed to fetch logs';
		}
	});
</script>

<main class="container mx-auto p-4">
	<h1 class="mb-4 text-3xl font-bold">Ultimi messaggi</h1>

	{#if error}
		<div class="text-red-500">{error}</div>
	{:else if logs.length === 0}
		<div>Loading...</div>
	{:else}
		<ul class="space-y-4">
			{#each logs as log}
				<li class="rounded-lg border bg-white p-4 shadow-md">
					<small><strong>ID:</strong> {log.id}</small>
					<h2 class="text-lg font-bold">{log.subject}</h2>
					<p><strong>Mittente:</strong> {log.sender}</p>
					<p><strong>Ricevuta il:</strong> {new Date(log.received_at).toLocaleString()}</p>

					{#if log.attachments}
						<div class="mt-2">
							<strong>Attachments:</strong>
							<pre>{JSON.stringify(log.attachments, null, 2)}</pre>
						</div>
					{/if}

					{#if log.body}
						<div class="mb-2 mt-2 rounded-lg border border-dotted border-gray-900 p-2">
							<p>{@html DOMPurify.sanitize(marked(log.body) as string)}</p>
						</div>
					{/if}

					{#if log.summary}
						<div class="mt-2">
							{#each log.summary as item}
								<div class="mb-2 rounded border border-dotted border-gray-900 p-2">
									<small><strong>Allegato:</strong> {item.file}</small>
									<div class="markdown-content">
										{@html DOMPurify.sanitize(marked(item.text) as string)}
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</li>
			{/each}
		</ul>
	{/if}
</main>

<style>
	.markdown-content {
		margin-top: 0.5rem;
		font-family: Arial, sans-serif;
		line-height: 1.6;
	}
</style>
