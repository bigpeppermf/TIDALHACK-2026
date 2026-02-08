import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import LatexEditorPanel from '@/components/convert/LatexEditorPanel.vue'

vi.mock('pdfjs-dist', () => ({
  GlobalWorkerOptions: { workerSrc: '' },
  getDocument: vi.fn(),
}))

vi.mock('vue-codemirror', () => ({
  Codemirror: {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template: '<textarea :value="modelValue" />',
  },
}))

function mountPanel() {
  return mount(LatexEditorPanel, {
    props: {
      modelValue: '\\section{Hello}',
      activeTab: 'source',
      copied: false,
      renderedPreview: '<p>preview</p>',
      zoom: 100,
      compileStatus: 'idle',
      compileStatusLabel: 'Ready',
      saveStatus: 'idle',
      saveStatusLabel: 'Auto Save',
    },
    global: { stubs: {} },
  })
}

describe('LatexEditorPanel', () => {
  it('emits recompile exactly once per click', async () => {
    const wrapper = mountPanel()
    const recompileButton = wrapper.findAll('button').find((button) => button.text() === 'Recompile')

    expect(recompileButton).toBeTruthy()
    if (!recompileButton) return

    await recompileButton.trigger('click')

    expect(wrapper.emitted('recompile')).toHaveLength(1)
  })

  it('clears PDF error text when error prop is reset', async () => {
    const wrapper = mountPanel()

    await wrapper.setProps({ activeTab: 'preview', pdfError: 'Session expired' })
    expect(wrapper.text()).toContain('Session expired')

    await wrapper.setProps({ pdfError: '' })
    expect(wrapper.text()).not.toContain('Session expired')
  })
})
