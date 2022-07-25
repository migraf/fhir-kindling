<script setup lang="ts">
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
import {ref, reactive} from 'vue';
import {Server} from "./domains/server/type";

const server = reactive<Server>({
  name: "",
  apiUrl: '',
  credentials: {
    username: '',
    password: '',
    token: '',
  }
});

</script>

<template>
  <div class="flex items-stretch">
    <div class="flex-col w-1/4">
      <h5 class="text-3xl font-bold">
        Server Configuration
      </h5>
      <p>{{ server.apiUrl }}</p>
      <p>{{ server.token }}</p>
    </div>
    <div class="flex-col w-3/4">
      <h1 class="text-3xl font-bold underline text-center">
        Hello world!
      </h1>
    </div>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
