<script lang="ts">
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	export let content: string;
</script>

<div class="mb-2 mt-2 rounded-lg border border-dotted border-gray-900 p-2">
	<p>{@html DOMPurify.sanitize(marked(content) as string)}</p>
</div>
