<template>
  <section class="page">
    <div>
      <h1 class="page__title">Dashboard</h1>
      <p class="page__subtitle">
        Übersicht für Lager, Warnungen und Einlagerung.
      </p>
    </div>

    <div class="hero-card">
      <h2 class="hero-card__title">THW Notfallversorgung</h2>
      <p class="hero-card__text">
        Aktueller Überblick über Vorräte, kritische Bestände und anstehende Maßnahmen.
      </p>

      <div class="hero-stats">
        <div class="hero-stat">
          <span class="hero-stat__label">Lager</span>
          <strong class="hero-stat__value">{{ stats.warehouseCount }}</strong>
        </div>
        <div class="hero-stat">
          <span class="hero-stat__label">Produkte</span>
          <strong class="hero-stat__value">{{ stats.productCount }}</strong>
        </div>
        <div class="hero-stat">
          <span class="hero-stat__label">Warnungen</span>
          <strong class="hero-stat__value">{{ counts.total }}</strong>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="card__title">Ortsverband</h2>
      <p class="card__text">Aktuell ausgewählter Ortsverband für die Demo.</p>
      <div class="top-space-sm">
        <select
  class="text-input"
  :value="selectedOrtsverband?.id ?? ''"
  @change="event => {
    const id = Number((event.target as HTMLSelectElement).value)
    const found = ortsverbaende.find(o => o.id === id)
    if (found) setSelectedOrtsverband(found)
  }"
>
  <option
    v-for="ortsverband in ortsverbaende"
    :key="ortsverband.id"
    :value="ortsverband.id"
  >
    {{ ortsverband.name }}
  </option>
</select>
      </div>
    </div>

    <div class="page-chip-row">
      <span class="page-chip">{{ counts.red }} MHD rot</span>
      <span class="page-chip">{{ counts.yellow }} MHD gelb</span>
      <span class="page-chip">{{ counts.stockLow }} Bestand kritisch</span>
    </div>

    <div>
      <div class="section-title">Schnellzugriffe</div>
      <div class="action-grid">
        <RouterLink to="/lager" class="action-button card-tap">
          <span class="action-button__title">Lager einsehen</span>
          <span class="action-button__text">Lager, Regale, Fächer und Produkte durchsuchen</span>
        </RouterLink>

        <RouterLink to="/einlagerung" class="action-button card-tap">
          <span class="action-button__title">Einlagerung</span>
          <span class="action-button__text">Barcode erfassen und Produkte einbuchen</span>
        </RouterLink>

        <RouterLink to="/rechner" class="action-button card-tap">
          <span class="action-button__title">Vorratsrechner</span>
          <span class="action-button__text">Deckungsgrad nach Personen und Tagen</span>
        </RouterLink>

        <RouterLink to="/warnungen" class="action-button card-tap">
          <span class="action-button__title">Warnungen</span>
          <span class="action-button__text">MHD- und Bestandsmeldungen prüfen</span>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="toolbar">
        <h2 class="card__title" style="margin: 0;">Dringend zu prüfen</h2>
        <RouterLink to="/warnungen" class="muted-small">Alle anzeigen</RouterLink>
      </div>

      <div v-if="loading" class="loading-state top-space-sm">
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
        <div>Warnungen werden geladen ...</div>
      </div>

      <div v-else-if="topAlerts.length" class="list-stack top-space-sm">
        <div
          v-for="alert in topAlerts"
          :key="alert.id"
          class="alert-row"
        >
          <div>
            <div class="alert-row__title">{{ alert.product.name }}</div>
            <div class="alert-row__text">
              {{ alert.warehouseName }} · {{ alert.shelfName }} · {{ alert.slotName }}
            </div>
          </div>

          <span class="inline-status" :class="statusClass(alert.type)">
            {{ statusLabel(alert.type, alert.daysUntilExpiry) }}
          </span>
        </div>
      </div>

      <div v-else class="empty-state top-space-sm">
        Keine aktiven Warnungen vorhanden.
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../services/api'
import type { AlertType, InventoryAlert, InventoryStats } from '../types'
import { getOrtsverbaende } from '../services/lagerApi'
import { useOrtsverbandStore } from '../stores/ortsverbandStore'
import type { Ortsverband } from '../types'

const loading = ref(true)

const ortsverbaende = ref<Ortsverband[]>([])

const {
  selectedOrtsverband,
  setSelectedOrtsverband,
  loadSelectedOrtsverband,
} = useOrtsverbandStore()

const stats = ref<InventoryStats>({
  warehouseCount: 0,
  shelfCount: 0,
  slotCount: 0,
  productCount: 0,
  totalUnits: 0,
})

const alerts = ref<InventoryAlert[]>([])

const counts = computed(() => ({
  total: alerts.value.length,
  red: alerts.value.filter((a) => a.type === 'mhd-red').length,
  yellow: alerts.value.filter((a) => a.type === 'mhd-yellow').length,
  stockLow: alerts.value.filter((a) => a.type === 'stock-low').length,
}))

const topAlerts = computed(() => alerts.value.slice(0, 4))

/* onMounted(async () => {
  loading.value = true
  stats.value = await api.getInventoryStats()
  alerts.value = await api.getInventoryAlerts()
  loading.value = false
}) */

onMounted(async () => {
  loading.value = true

  loadSelectedOrtsverband()

  ortsverbaende.value = await getOrtsverbaende()

  if (!selectedOrtsverband.value && ortsverbaende.value.length > 0) {
    setSelectedOrtsverband(ortsverbaende.value[0])
  }

  stats.value = await api.getInventoryStats()
  alerts.value = await api.getInventoryAlerts()

  loading.value = false
})

function statusClass(type: AlertType): string {
  if (type === 'mhd-red') return 'inline-status--danger'
  if (type === 'mhd-yellow') return 'inline-status--warning'
  return 'inline-status--danger'
}

function statusLabel(type: AlertType, days?: number): string {
  if (type === 'mhd-red') return `MHD rot${typeof days === 'number' ? ` · ${days} Tage` : ''}`
  if (type === 'mhd-yellow') return `MHD gelb${typeof days === 'number' ? ` · ${days} Tage` : ''}`
  return 'Bestand kritisch'
}
</script>