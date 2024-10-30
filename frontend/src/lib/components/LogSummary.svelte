<script lang="ts">
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';
	import type { Log } from '../../types.js';
	export let summary: Log['summary'];
</script>

<div class="mt-2">
	{#each summary as item}
		<div class="mb-2 rounded border border-dotted border-gray-900 p-2">
			<small><strong>Allegato:</strong> {item.file}</small>
			<div class="markdown-content">
				{@html DOMPurify.sanitize(marked(item.text) as string)}
			</div>
		</div>
	{/each}
</div>

<style>
	.markdown-content {
		margin-top: 0.5rem;
		font-family: Arial, sans-serif;
		line-height: 1.6;
	}
</style>
