<template>
  <section class="page">
    <div>
      <h1 class="page__title">Warnungen</h1>
      <p class="page__subtitle">
        Automatisch erkannte MHD-Warnungen für den ausgewählten Ortsverband.
      </p>
    </div>

    <div class="soft-card" v-if="selectedOrtsverband">
      <h3 class="soft-card__title">Aktueller Ortsverband</h3>
      <p class="soft-card__text">{{ selectedOrtsverband.name }}</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-card__label">Gesamt</span>
        <strong class="stat-card__value">{{ visibleWarnings.length }}</strong>
      </div>

      <div class="stat-card">
        <span class="stat-card__label">Abgelaufen</span>
        <strong class="stat-card__value">
          {{ visibleWarnings.filter((w) => w.status === 'expired').length }}
        </strong>
      </div>

      <div class="stat-card">
        <span class="stat-card__label">Kritisch</span>
        <strong class="stat-card__value">
          {{ visibleWarnings.filter((w) => w.status === 'critical').length }}
        </strong>
      </div>

      <div class="stat-card">
        <span class="stat-card__label">Warnung</span>
        <strong class="stat-card__value">
          {{ visibleWarnings.filter((w) => w.status === 'warning').length }}
        </strong>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
      <div>Warnungen werden geladen ...</div>
    </div>

    <div v-else-if="errorMessage" class="empty-state">
      {{ errorMessage }}

      <div class="top-space-sm">
        <RouterLink to="/" class="primary-button" style="display: inline-block;">
          Zum Dashboard
        </RouterLink>
      </div>
    </div>

    <div v-else-if="visibleWarnings.length" class="list-stack">
      <div
        v-for="warning in visibleWarnings"
        :key="warning.stock_id"
        class="card"
        :class="cardClass(warning.status)"
      >
        <div class="alert-card__top">
          <div>
            <h2 class="card__title" style="margin-bottom: 4px;">
              {{ warning.name }}
            </h2>
            <p class="card__text">
              {{ warning.brand ?? 'Keine Marke' }} · {{ warning.warehouse_name }}
            </p>
          </div>

          <span class="inline-status" :class="statusClass(warning.status)">
            {{ statusLabel(warning.status) }}
          </span>
        </div>

        <div class="alert-detail-grid">
          <div>
            <span class="alert-detail-grid__label">MHD</span>
            <strong>{{ warning.best_before ?? 'Kein MHD' }}</strong>
          </div>

          <div>
            <span class="alert-detail-grid__label">Resttage</span>
            <strong>{{ warning.days_left ?? '–' }}</strong>
          </div>

          <div>
            <span class="alert-detail-grid__label">Stock-ID</span>
            <strong>{{ warning.stock_id }}</strong>
          </div>

          <div>
            <span class="alert-detail-grid__label">Produkt-ID</span>
            <strong>{{ warning.product_id }}</strong>
          </div>
        </div>

        <p class="card__text" style="margin-top: 12px;">
          {{ description(warning.status, warning.days_left) }}
        </p>

        <div class="text-right top-space-sm">
          <button
            class="back-button"
            type="button"
            @click="acknowledge(warning.stock_id)"
          >
            Zur Kenntnis genommen
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      Keine aktiven MHD-Warnungen vorhanden.
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  getExpiringProductsByOrtsverband,
  type ExpiringProduct,
} from '../services/warnungenApi'
import { useOrtsverbandStore } from '../stores/ortsverbandStore'

const loading = ref(true)
const errorMessage = ref('')
const warnings = ref<ExpiringProduct[]>([])
const dismissedIds = ref<number[]>([])

const {
  selectedOrtsverband,
  loadSelectedOrtsverband,
} = useOrtsverbandStore()

const visibleWarnings = computed(() =>
  warnings.value.filter((warning) => !dismissedIds.value.includes(warning.stock_id)),
)

onMounted(async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    loadSelectedOrtsverband()

    if (!selectedOrtsverband.value) {
      errorMessage.value = 'Bitte zuerst im Dashboard einen Ortsverband auswählen.'
      return
    }

    warnings.value = await getExpiringProductsByOrtsverband(
      selectedOrtsverband.value.id,
      30,
    )
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Warnungen konnten nicht geladen werden.'
  } finally {
    loading.value = false
  }
})

function acknowledge(stockId: number): void {
  dismissedIds.value.push(stockId)
}

function statusClass(status: ExpiringProduct['status']): string {
  if (status === 'expired') return 'inline-status--danger'
  if (status === 'critical') return 'inline-status--danger'
  if (status === 'warning') return 'inline-status--warning'
  return 'inline-status--success'
}

function statusLabel(status: ExpiringProduct['status']): string {
  if (status === 'expired') return 'Abgelaufen'
  if (status === 'critical') return 'Kritisch'
  if (status === 'warning') return 'MHD-Warnung'
  if (status === 'ok') return 'OK'
  return 'Unbekannt'
}

function cardClass(status: ExpiringProduct['status']): string {
  if (status === 'expired') return 'alert-card alert-card--danger'
  if (status === 'critical') return 'alert-card alert-card--danger'
  if (status === 'warning') return 'alert-card alert-card--warning'
  return 'alert-card'
}

function description(status: ExpiringProduct['status'], daysLeft: number | null): string {
  if (status === 'expired') {
    return 'Dieses Produkt ist bereits abgelaufen und sollte sofort geprüft oder ausgesondert werden.'
  }

  if (status === 'critical') {
    return `Dieses Produkt läuft sehr bald ab${typeof daysLeft === 'number' ? `, aktuell in ${daysLeft} Tagen` : ''}. Sofort prüfen und bevorzugt verbrauchen.`
  }

  if (status === 'warning') {
    return `Dieses Produkt läuft bald ab${typeof daysLeft === 'number' ? `, aktuell in ${daysLeft} Tagen` : ''}. Zeitnah Verbrauch oder Ersatz planen.`
  }

  return 'Dieses Produkt liegt aktuell noch im unkritischen Bereich.'
}
</script>