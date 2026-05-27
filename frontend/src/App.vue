<template>
  <div class="app-shell">
    <header class="top-bar">
      <div class="top-bar__title">THW Notfallversorgung</div>
      <div class="top-bar__subtitle">Mobile Lager- und Vorratsverwaltung</div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <nav class="bottom-nav">
      <RouterLink to="/" class="bottom-nav__item">Home</RouterLink>
      <RouterLink to="/lager" class="bottom-nav__item">Lager</RouterLink>
      <RouterLink to="/einlagerung" class="bottom-nav__item">Scan</RouterLink>
      <RouterLink to="/warnungen" class="bottom-nav__item">Warnungen</RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
</script>