 /* global mermaid, svgPanZoom, canvg */

 const state = {
   active: 'er',
   panZoom: {
     er: null,
     uml: null,
   },
 }

 function $(id) {
   return document.getElementById(id)
 }

 function setActive(tab) {
   state.active = tab

   const isER = tab === 'er'
   $('tab-er').classList.toggle('is-active', isER)
   $('tab-uml').classList.toggle('is-active', !isER)
   $('tab-er').setAttribute('aria-selected', String(isER))
   $('tab-uml').setAttribute('aria-selected', String(!isER))

   $('panel-er').classList.toggle('is-active', isER)
   $('panel-uml').classList.toggle('is-active', !isER)

   requestAnimationFrame(() => {
     fit()
   })
 }

 function getActiveSvg() {
   const container = state.active === 'er' ? $('er') : $('uml')
   return container.querySelector('svg')
 }

 function ensurePanZoom() {
   const svg = getActiveSvg()
   if (!svg) return null

   const key = state.active
   if (state.panZoom[key]) return state.panZoom[key]

   const instance = svgPanZoom(svg, {
     zoomEnabled: true,
     controlIconsEnabled: false,
     fit: true,
     center: true,
     minZoom: 0.15,
     maxZoom: 20,
     zoomScaleSensitivity: 0.25,
     dblClickZoomEnabled: true,
     mouseWheelZoomEnabled: true,
     preventMouseEventsDefault: true,
   })

   state.panZoom[key] = instance
   return instance
 }

 function fit() {
   const pz = ensurePanZoom()
   if (!pz) return
   try {
     pz.resize()
     pz.fit()
     pz.center()
   } catch (e) {
     // svg-pan-zoom може кинути помилку, якщо svg ще не готовий
   }
 }

 function openExportMenu() {
   const menu = $('export-menu')
   const btn = $('btn-export')
   const isOpen = menu.classList.toggle('is-open')
   btn.setAttribute('aria-expanded', String(isOpen))
 }

 function closeExportMenu() {
   const menu = $('export-menu')
   const btn = $('btn-export')
   menu.classList.remove('is-open')
   btn.setAttribute('aria-expanded', 'false')
 }

 function downloadBlob(filename, blob) {
   const url = URL.createObjectURL(blob)
   const a = document.createElement('a')
   a.href = url
   a.download = filename
   document.body.appendChild(a)
   a.click()
   a.remove()
   URL.revokeObjectURL(url)
 }

 function getExportBaseName() {
   return state.active === 'er' ? 'flappy-bird-db-er' : 'flappy-bird-uml-class'
 }

 function svgToCleanString(svgEl) {
   const clone = svgEl.cloneNode(true)
   const svg = /** @type {SVGElement} */ (clone)

   svg.removeAttribute('style')
   svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
   svg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')

   const currentViewBox = svg.getAttribute('viewBox')
   if (!currentViewBox) {
     const box = svgEl.getBBox()
     svg.setAttribute('viewBox', `${box.x} ${box.y} ${box.width} ${box.height}`)
   }

   const serializer = new XMLSerializer()
   return serializer.serializeToString(svg)
 }

 async function exportSvg() {
   const svgEl = getActiveSvg()
   if (!svgEl) return
   const xml = svgToCleanString(svgEl)
   const blob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' })
   downloadBlob(`${getExportBaseName()}.svg`, blob)
 }

 async function exportPng() {
   const svgEl = getActiveSvg()
   if (!svgEl) return

   const xml = svgToCleanString(svgEl)
   const viewBox = svgEl.viewBox && svgEl.viewBox.baseVal
   const width = Math.max(1400, Math.floor(viewBox?.width || svgEl.clientWidth || 1400))
   const height = Math.max(900, Math.floor(viewBox?.height || svgEl.clientHeight || 900))

   const canvas = document.createElement('canvas')
   const scale = 2
   canvas.width = width * scale
   canvas.height = height * scale
   const ctx = canvas.getContext('2d')
   if (!ctx) return

   ctx.setTransform(scale, 0, 0, scale, 0, 0)
   ctx.clearRect(0, 0, width, height)
   ctx.fillStyle = '#ffffff'
   ctx.fillRect(0, 0, width, height)

   const v = await canvg.Canvg.fromString(ctx, xml, {
     ignoreMouse: true,
     ignoreAnimation: true,
   })
   await v.render()

   const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'))
   if (!blob) return
   downloadBlob(`${getExportBaseName()}.png`, blob)
 }

 function wireUi() {
   $('tab-er').addEventListener('click', () => setActive('er'))
   $('tab-uml').addEventListener('click', () => setActive('uml'))

   $('btn-fit').addEventListener('click', () => fit())

   $('btn-export').addEventListener('click', (e) => {
     e.stopPropagation()
     openExportMenu()
   })

   $('export-menu').addEventListener('click', async (e) => {
     const t = /** @type {HTMLElement} */ (e.target)
     const type = t?.dataset?.export
     if (!type) return
     closeExportMenu()
     if (type === 'svg') await exportSvg()
     if (type === 'png') await exportPng()
   })

   document.addEventListener('click', () => closeExportMenu())
   document.addEventListener('keydown', (e) => {
     if (e.key === 'Escape') closeExportMenu()
   })

   window.addEventListener('resize', () => fit())
 }

 function initMermaid() {
   mermaid.initialize({
     startOnLoad: false,
     securityLevel: 'loose',
     theme: 'neutral',
     fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial',
     flowchart: {
       curve: 'linear',
       defaultRenderer: 'elk',
     },
     er: {
       useMaxWidth: true,
     },
     class: {
       useMaxWidth: true,
     },
     themeVariables: {
       background: '#ffffff',
       primaryColor: '#ffffff',
       primaryBorderColor: '#111111',
       primaryTextColor: '#111111',
       secondaryColor: '#ffffff',
       tertiaryColor: '#ffffff',
       lineColor: '#111111',
       textColor: '#111111',
       fontSize: '12px',
     },
   })
 }

 async function renderAll() {
   const er = $('er')
   const uml = $('uml')

   const erCode = er.textContent
   const umlCode = uml.textContent

   er.textContent = ''
   uml.textContent = ''

   const erSvg = await mermaid.render('mermaid-er-flappy', erCode)
   er.innerHTML = erSvg.svg

   const umlSvg = await mermaid.render('mermaid-uml-flappy', umlCode)
   uml.innerHTML = umlSvg.svg

   state.panZoom.er = null
   state.panZoom.uml = null

   ensurePanZoom()
   setTimeout(() => fit(), 0)
 }

 async function main() {
   initMermaid()
   wireUi()
   await renderAll()
   setActive('er')
 }

 main().catch((e) => {
   const footer = document.querySelector('.footer__left')
   if (footer) {
     footer.innerHTML = `<span class="dot"></span><span style="color: rgba(255,93,93,0.95)">Помилка рендеру діаграм: ${String(e?.message || e)}</span>`
   }
 })

