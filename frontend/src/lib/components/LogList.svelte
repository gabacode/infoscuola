<script lang="ts">
	import type { Log } from '../../types.js';
	import { onMount } from 'svelte';
	import { fetchLogs } from '$lib/api.js';
	import LogItem from './LogItem.svelte';

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
				<LogItem {log} />
			{/each}
		</ul>
	{/if}
</main>
