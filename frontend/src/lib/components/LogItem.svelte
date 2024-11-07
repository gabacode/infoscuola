<script lang="ts">
	import type { Log } from '../../types.js';
	import LogContent from './LogContent.svelte';
	import LogSummary from './LogSummary.svelte';

	export let log: Log;
	export const date = new Date(log.received_at).toLocaleString();
</script>

<li class="rounded-lg border bg-white p-4 shadow-md">
	<div>
		<small><strong>ID:</strong> {log.id}</small>
		<h2 class="text-lg font-bold">{log.subject}</h2>
	</div>
	<div>
		<small class="block"><strong>Mittente:</strong> {log.sender}</small>
		<small class="block"><strong>Ricevuta il:</strong> {date}</small>
	</div>

	{#if log.body}
		<LogContent content={log.body} />
	{/if}

	{#if log.summary}
		<LogSummary summary={log.summary} />
	{/if}
</li>
