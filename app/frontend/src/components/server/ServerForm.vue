<script setup lang="ts">
import {Server} from "../../domains/server/type";
import {ref, reactive} from "vue";
import {setServer} from "../../domains/server/api";

interface ServerState {
  state?: string;
  server?: Server;
}

const server = defineProps<ServerState>()

const formState = reactive({
  serverState: server.state,
  serverForm: server.server? server.server : {
    name: "",
    api_url: "",
    credentials: {
      username: "",
      password: "",
      token: "",
    },
  },
  authMode: 'basic',
})

const emits = defineEmits(["serverChanged"])

async function onSubmit() {
  console.log("onSubmit", formState.serverForm);
  emits("serverChanged", formState.serverForm);
  const resp = await setServer(formState.serverForm);
  console.log(resp)
  formState.serverState = "success";

}

</script>
<template>
  <div class="flex-col bg-gray-800 rounded shadow-cyan-900">
    <h5 class="text-3xl font-bold text-center text-gray-100 font-mono pt-2">
      Server Configuration
    </h5>
    <div
        v-if="formState.serverState === 'success'"
        class="text-green-700 text-xl text-center"
    >
      connected
    </div>
    <div class="w-full ">
      <form class="shadow-md rounded px-8 pt-6 pb-8 mb-4">
        <div class="mb-4">
          <label class="block text-gray-100 text-sm font-bold mb-2" for="address">
            API Address
          </label>
          <input
              class="shadow bg-gray-600 placeholder-gray-200 appearance-none border rounded w-full py-2 px-3 text-gray-100 leading-tight focus:outline-blue-600 focus:shadow-outline"
              id="address"
              type="text"
              placeholder="https://example.com/fhir"
              v-model="formState.serverForm.api_url"
          >
        </div>
        <div class="flex-col mb-6 w-full">
          <label class="block text-gray-100 text-sm font-bold mb-2" for="auth-mode">
            Authentication
          </label>
          <div class="grid grid-flow-col grid-flow-row gap-4 auto-cols-auto flex-grow justify-between">
            <div class="items-center">
              <input
                  :checked="formState.authMode === 'basic'"
                  id="radio-basic-auth"
                  v-model="formState.authMode"
                  type="radio"
                  value="basic"
                  name="radio-basic-auth"
                  class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              >
              <label
                  for="radio-basic-auth"
                  class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
              >
                Basic
              </label>
            </div>
            <div class="items-center">
              <input
                  id="radio-token-auth"
                  v-model="formState.authMode"
                  :checked="formState.authMode === 'token'"
                  type="radio"
                  value="token"
                  name="radio-token-auth"
                  class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              >
              <label
                  for="radio-token-auth"
                  class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
              >
                Token
              </label>
            </div>
            <div class="items-center">
              <input
                  id="radio-oidc-auth"
                  disabled
                  v-model="formState.authMode"
                  :checked="formState.authMode === 'oidc'"
                  type="radio"
                  value="oidc"
                  name="inline-radio-group"
                  class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              >
              <label
                  for="radio-oidc-auth"
                  class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
              >
                OIDC
              </label>
            </div>
            <div class="items-center">
              <input
                  id="radio-no-auth"
                  v-model="formState.authMode"
                  :checked="formState.authMode === 'none'"
                  type="radio"
                  value="oidc"
                  name="inline-radio-group"
                  class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              >
              <label
                  for="radio-no-auth"
                  class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
              >
                None
              </label>
            </div>
          </div>
        </div>
        <div
            class="mb-6"
            v-if="formState.authMode === 'basic'"
        >
          <label class="block text-gray-100 text-sm font-bold mb-2" for="username">
            Username
          </label>
          <input
              class="shadow mb-4 bg-gray-600 placeholder-gray-200 appearance-none border rounded w-full py-2 px-3 text-gray-100 leading-tight focus:outline-blue-600 focus:shadow-outline"
              id="username"
              type="text"
              placeholder="Username"
              v-model="formState.serverForm.credentials.username"
          >
          <label class="block text-gray-100 text-sm font-bold mb-2" for="username">
            Password
          </label>
          <input
              class="shadow bg-gray-600 placeholder-gray-200 appearance-none border rounded w-full py-2 px-3 text-gray-100 leading-tight focus:outline-blue-600 focus:shadow-outline"
              id="password"
              type="password"
              placeholder="Password"
              v-model="formState.serverForm.credentials.password"
          >

        </div>
        <div
            class="mb-6"
            v-if="formState.authMode === 'token'"
        >
          <label class="block text-gray-100 text-sm font-bold mb-2" for="token">
            Token
          </label>
          <input
              class="shadow bg-gray-600 placeholder-gray-200 appearance-none border rounded w-full py-2 px-3 text-gray-100 leading-tight focus:outline-blue-600 focus:shadow-outline"
              id="token"
              type="password"
              placeholder="Token"
              v-model="formState.serverForm.credentials.token"
          >

        </div>


        <div class="flex items-center justify-between">
          <button
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-600"
              type="button"
              @click="onSubmit"
              :disabled="formState.serverState === 'success'"
          >
            Connect
          </button>
          <font-awesome-icon icon="fa-solid fa-link-horizontal" class="text-gray-100" size="lg" inverse/>
          <button
              class="bg-cyan-700 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              type="button"
              @click="formState.serverState = 'editing'"
              v-if="formState.serverState === 'success'"
          >
            Edit
          </button>

        </div>
      </form>
    </div>
  </div>

</template>

<style scoped>

</style>
