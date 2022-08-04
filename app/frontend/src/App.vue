<script setup lang="ts">
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
import {ref, reactive} from 'vue';
import {Server} from "./domains/server/type";
import QueryBuilder from './components/query/QueryBuilder.vue';
import QueryHeader from "./components/query/ResourceQuery.vue";
import ServerForm from "./components/server/ServerForm.vue";

const server = reactive<Server>({
  name: "",
  api_url: '',
  credentials: {
    username: '',
    password: '',
    token: '',
  }
});

function handleServerChanged(s: Server){
  console.log("handleServerChanged", s);
}
</script>

<template>
  <div class="flex items-stretch h-screen bg-gray-900 text-gray-200 divide-x divide-gray-500">
    <div class="flex-col w-1/5 h-screen">
      <ServerForm
          :server="server"
          @serverChanged="handleServerChanged"
      >

      </ServerForm>
    </div>
    <div class="flex-col w-4/5">
      <div class="flex-row">
        <h1 class="text-3xl font-bold underline text-center font-mono">
          Query Builder
        </h1>
      </div>
      <div class="flex-row">
        <Suspense>
          <div>
            <QueryBuilder/>
          </div>
          <template #fallback>
            <div>Loading...</div>
          </template>
        </Suspense>

      </div>
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
