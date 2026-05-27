import { ref } from 'vue'
import type { Ortsverband } from '../types'

const selectedOrtsverband = ref<Ortsverband | null>(null)

export function useOrtsverbandStore() {
  function setSelectedOrtsverband(ortsverband: Ortsverband) {
    selectedOrtsverband.value = ortsverband
    localStorage.setItem('selectedOrtsverband', JSON.stringify(ortsverband))
  }

  function loadSelectedOrtsverband() {
    const saved = localStorage.getItem('selectedOrtsverband')
    if (saved) {
      selectedOrtsverband.value = JSON.parse(saved)
    }
  }

  return {
    selectedOrtsverband,
    setSelectedOrtsverband,
    loadSelectedOrtsverband,
  }
}