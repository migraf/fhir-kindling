<script lang="ts">
	import { TabContent, TabPane } from 'sveltestrap';
	import FhirQuery from "./query/FhirQuery.svelte";
	export let name: string;
	export let mode: string = "query";
</script>
<svelte:head>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
</svelte:head>
<main>

	<h1>Welcome to FHIR Kindling {name}!</h1>
	<TabContent vertical pills>
		<TabPane tabId="query" tab="Query" active>
			<FhirQuery>

			</FhirQuery>
		</TabPane>
		<TabPane tabId="bravo" tab="Servers">
			<h2>Bravo</h2>
			<img
					alt="Johnny Bravo"
					src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Johnny_Bravo_series_logo.png/320px-Johnny_Bravo_series_logo.png"
			/>
		</TabPane>
		<TabPane tabId="charlie" tab="Charlie">
			<h2>Charlie</h2>
			<img
					alt="Charlie Brown"
					src="https://upload.wikimedia.org/wikipedia/en/2/22/Charlie_Brown.png"
			/>
		</TabPane>
	</TabContent>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
