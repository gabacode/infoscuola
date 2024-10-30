<script lang="ts">
	import type { Log } from '../../types.js';
	import LogContent from './LogContent.svelte';
	import LogSummary from './LogSummary.svelte';

	export let log: Log;
</script>

<li class="rounded-lg border bg-white p-4 shadow-md">
	<small><strong>ID:</strong> {log.id}</small>
	<h2 class="text-lg font-bold">{log.subject}</h2>
	<p><strong>Mittente:</strong> {log.sender}</p>
	<p><strong>Ricevuta il:</strong> {new Date(log.received_at).toLocaleString()}</p>

	{#if log.body}
		<LogContent content={log.body} />
	{/if}

	{#if log.summary}
		<LogSummary summary={log.summary} />
	{/if}
</li>
