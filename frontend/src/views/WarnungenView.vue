<template>
  <section class="page">
    <div>
      <h1 class="page__title">Warnungen</h1>
      <p class="page__subtitle">
        Automatisch erkannte MHD- und Mindestbestandswarnungen.
      </p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-card__label">Gesamt</span>
        <strong class="stat-card__value">{{ visibleAlerts.length }}</strong>
      </div>
      <div class="stat-card">
        <span class="stat-card__label">MHD rot</span>
        <strong class="stat-card__value">{{ visibleAlerts.filter((a) => a.type === 'mhd-red').length }}</strong>
      </div>
      <div class="stat-card">
        <span class="stat-card__label">MHD gelb</span>
        <strong class="stat-card__value">{{ visibleAlerts.filter((a) => a.type === 'mhd-yellow').length }}</strong>
      </div>
      <div class="stat-card">
        <span class="stat-card__label">Bestand</span>
        <strong class="stat-card__value">{{ visibleAlerts.filter((a) => a.type === 'stock-low').length }}</strong>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
      <div>Warnungen werden geladen ...</div>
    </div>

    <div v-else-if="visibleAlerts.length" class="list-stack">
      <div
        v-for="alert in visibleAlerts"
        :key="alert.id"
        class="card"
        :class="cardClass(alert.type)"
      >
        <div class="alert-card__top">
          <div>
            <h2 class="card__title" style="margin-bottom: 4px;">{{ alert.product.name }}</h2>
            <p class="card__text">
              {{ alert.warehouseName }} · {{ alert.shelfName }} · {{ alert.slotName }}
            </p>
          </div>

          <span class="inline-status" :class="statusClass(alert.type)">
            {{ statusLabel(alert.type) }}
          </span>
        </div>

        <div class="alert-detail-grid">
          <div>
            <span class="alert-detail-grid__label">Restmenge</span>
            <strong>{{ alert.product.menge }}</strong>
          </div>
          <div>
            <span class="alert-detail-grid__label">Schwelle</span>
            <strong>{{ alert.product.threshold }}</strong>
          </div>
          <div>
            <span class="alert-detail-grid__label">MHD</span>
            <strong>{{ alert.product.mhd }}</strong>
          </div>
          <div v-if="typeof alert.daysUntilExpiry === 'number'">
            <span class="alert-detail-grid__label">Resttage</span>
            <strong>{{ alert.daysUntilExpiry }}</strong>
          </div>
        </div>

        <p class="card__text" style="margin-top: 12px;">
          {{ description(alert.type, alert.daysUntilExpiry) }}
        </p>

        <div class="text-right top-space-sm">
          <button class="back-button" type="button" @click="acknowledge(alert.id)">
            Zur Kenntnis genommen
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      Keine aktiven Warnungen vorhanden.
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../services/api'
import type { AlertType, InventoryAlert } from '../types'

const loading = ref(true)
const alerts = ref<InventoryAlert[]>([])
const dismissedIds = ref<string[]>([])

const visibleAlerts = computed(() =>
  alerts.value.filter((alert) => !dismissedIds.value.includes(alert.id)),
)

onMounted(async () => {
  loading.value = true
  alerts.value = await api.getInventoryAlerts()
  loading.value = false
})

async function acknowledge(alertId: string): Promise<void> {
  await api.acknowledgeAlert(alertId)
  dismissedIds.value.push(alertId)
}

function statusClass(type: AlertType): string {
  if (type === 'mhd-red') return 'inline-status--danger'
  if (type === 'mhd-yellow') return 'inline-status--warning'
  return 'inline-status--danger'
}

function statusLabel(type: AlertType): string {
  if (type === 'mhd-red') return 'MHD rot'
  if (type === 'mhd-yellow') return 'MHD gelb'
  return 'Bestand kritisch'
}

function cardClass(type: AlertType): string {
  if (type === 'mhd-red') return 'alert-card alert-card--danger'
  if (type === 'mhd-yellow') return 'alert-card alert-card--warning'
  return 'alert-card alert-card--danger'
}

function description(type: AlertType, days?: number): string {
  if (type === 'mhd-red') {
    return `Dieses Produkt läuft in weniger als 30 Tagen ab${typeof days === 'number' ? `, aktuell in ${days} Tagen` : ''}. Sofort prüfen und bevorzugt verbrauchen oder austauschen.`
  }

  if (type === 'mhd-yellow') {
    return `Dieses Produkt läuft in weniger als 90 Tagen ab${typeof days === 'number' ? `, aktuell in ${days} Tagen` : ''}. Zeitnah Verbrauch oder Ersatz planen.`
  }

  return 'Der aktuelle Bestand liegt unter dem definierten Mindestbestand. Nachbestellung oder Umlagerung prüfen.'
}
</script>