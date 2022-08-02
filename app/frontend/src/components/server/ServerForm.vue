<script setup lang="ts">
import {Server} from "../../domains/server/type";
import {ref, reactive} from "vue";

interface ServerState {
  state: string;
  server?: Server;
}
const server = defineProps<ServerState>()

const edit = ref(false);


</script>
<template>
  <div class="">

  </div>

</template>

<style scoped>

</style>
