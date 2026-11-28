<script setup lang="ts">
import Sidebar from "@/components/Sidebar.vue";
</script>

<template>
  <div class="dashboard">
    <Sidebar :title="'Admin Dashboard'">
      <template v-slot:entries> </template>
    </Sidebar>
  </div>
</template>

<style scoped src="../assets/admin.css"></style>
