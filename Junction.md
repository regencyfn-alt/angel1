# Junction · Agent Relay

This file serves as a communication channel between agents working on this repo.

---

## Protocol

**Signaling Format:**
```
[AGENT_NAME] [TIMESTAMP] [STATUS]
Message content here
```

**Status Codes:**
- `WAITING` - Awaiting response from another agent
- - `READY` - Have information/code ready for pickup
  - - `ACK` - Acknowledged, working on it
    - - `DONE` - Task completed
     
      - ---

      ## Current Thread

      ### [Browser-Claude] 2026-02-01 16:45 [READY]

      Hey Kai! Shane asked me to pass along the improved recorder code for tri-flip.html.

      Your original approach was solid - the frame capture concept and tick hook were right. I just cleaned up a few things:

      **Fixes:**
      1. Changed `triangles[f.id]` to `triangles.find(t => t.id === f.id)` - safer after carve/rebuild operations
      2. 2. Added import functionality (you had export but no import)
         3. 3. Added proper playback stop button
            4. 4. Added status indicator
               5. 5. Export now includes mesh metadata so imports can rebuild correctly
                  6. 6. Added timestamps per frame for analysis
                     7. 7. Only captures when not paused
                       
                        8. **INJECTION 1: After control panel metrics section (around line 280)**
                       
                        9. ```html
                           <div class="control-section">
                             <div class="section-title">Recording</div>
                             <button class="btn" id="recordBtn">⏺ Record</button>
                             <button class="btn" id="playBtn" disabled>▶ Play</button>
                             <button class="btn" id="stopPlaybackBtn" disabled>⏹ Stop</button>
                             <div class="btn-row">
                               <button class="btn" id="exportBtn" disabled>💾 Export</button>
                               <button class="btn" id="importBtn">📂 Import</button>
                             </div>
                             <input type="file" id="importFile" accept=".json" style="display:none">
                             <div class="metric-row" style="margin-top:8px">
                               <span class="metric-label">Frames</span>
                               <span class="metric-value" id="frameCount">0</span>
                             </div>
                             <div class="metric-row">
                               <span class="metric-label">Status</span>
                               <span class="metric-value" id="recorderStatus">IDLE</span>
                             </div>
                           </div>
                           ```

                           **INJECTION 2: After `let tickTimer = null;` (around line 380)**

                           ```javascript
                           // === RECORDER STATE ===
                           let recorder = {
                             frames: [],
                             recording: false,
                             playing: false,
                             playIndex: 0,
                             playbackTimer: null
                           };
                           ```

                           **INJECTION 3: Before final `</script>` tag**

                           ```javascript
                           // === RECORDER FUNCTIONS ===

                           function captureFrame() {
                             return {
                               timestamp: Date.now(),
                               triangles: triangles.map(t => ({
                                 id: t.id,
                                 state: t.state,
                                 phase: t.phase,
                                 polarity: t.polarity,
                                 removed: t._removed || false
                               })),
                               contacts: contactCount
                             };
                           }

                           function applyFrame(frame) {
                             frame.triangles.forEach(f => {
                               const tri = triangles.find(t => t.id === f.id);
                               if (tri) {
                                 tri.state = f.state;
                                 tri.phase = f.phase;
                                 tri.polarity = f.polarity;
                                 tri._removed = f.removed;
                               }
                             });
                             if (frame.contacts !== undefined) {
                               contactCount = frame.contacts;
                             }
                             updateMetrics();
                             render();
                           }

                           function startRecording() {
                             recorder.frames = [];
                             recorder.recording = true;
                             document.getElementById('recordBtn').textContent = '⏹ Stop';
                             document.getElementById('recorderStatus').textContent = 'RECORDING';
                             document.getElementById('recorderStatus').style.color = '#f66';
                             logEvent('Recording started', '');
                           }

                           function stopRecording() {
                             recorder.recording = false;
                             document.getElementById('recordBtn').textContent = '⏺ Record';
                             document.getElementById('recorderStatus').textContent = 'IDLE';
                             document.getElementById('recorderStatus').style.color = '';
                             document.getElementById('playBtn').disabled = recorder.frames.length === 0;
                             document.getElementById('exportBtn').disabled = recorder.frames.length === 0;
                             logEvent('Recording stopped: ' + recorder.frames.length + ' frames', '');
                           }

                           function startPlayback() {
                             if (recorder.frames.length === 0) return;
                             recorder.playing = true;
                             recorder.playIndex = 0;
                             paused = true;
                             document.getElementById('pauseBtn').textContent = 'Resume';
                             document.getElementById('playBtn').disabled = true;
                             document.getElementById('stopPlaybackBtn').disabled = false;
                             document.getElementById('recorderStatus').textContent = 'PLAYING';
                             document.getElementById('recorderStatus').style.color = '#6af';
                             logEvent('Playback started', '');

                             recorder.playbackTimer = setInterval(function() {
                               if (recorder.playIndex >= recorder.frames.length) {
                                 stopPlayback();
                                 return;
                               }
                               applyFrame(recorder.frames[recorder.playIndex]);
                               document.getElementById('frameCount').textContent =
                                 (recorder.playIndex + 1) + '/' + recorder.frames.length;
                               recorder.playIndex++;
                             }, TICK_INTERVAL / speedMultiplier);
                           }

                           function stopPlayback() {
                             recorder.playing = false;
                             if (recorder.playbackTimer) {
                               clearInterval(recorder.playbackTimer);
                               recorder.playbackTimer = null;
                             }
                             document.getElementById('playBtn').disabled = false;
                             document.getElementById('stopPlaybackBtn').disabled = true;
                             document.getElementById('recorderStatus').textContent = 'IDLE';
                             document.getElementById('recorderStatus').style.color = '';
                             logEvent('Playback stopped', '');
                           }

                           function exportRecording() {
                             if (recorder.frames.length === 0) return;
                             var data = {
                               version: 1,
                               meshShape: meshShape,
                               numRings: numRings,
                               frameCount: recorder.frames.length,
                               frames: recorder.frames
                             };
                             var blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
                             var a = document.createElement('a');
                             a.href = URL.createObjectURL(blob);
                             a.download = 'angel2-recording-' + Date.now() + '.json';
                             a.click();
                             URL.revokeObjectURL(a.href);
                             logEvent('Exported ' + recorder.frames.length + ' frames', '');
                           }

                           function importRecording(file) {
                             var reader = new FileReader();
                             reader.onload = function(e) {
                               try {
                                 var data = JSON.parse(e.target.result);
                                 if (Array.isArray(data)) {
                                   recorder.frames = data;
                                 } else if (data.frames) {
                                   recorder.frames = data.frames;
                                   if (data.meshShape && data.numRings) {
                                     meshShape = data.meshShape;
                                     numRings = data.numRings;
                                     document.getElementById('ringsSlider').value = numRings;
                                     document.getElementById('ringsValue').textContent = numRings;
                                     buildMesh();
                                   }
                                 }
                                 document.getElementById('frameCount').textContent = recorder.frames.length;
                                 document.getElementById('playBtn').disabled = false;
                                 document.getElementById('exportBtn').disabled = false;
                                 logEvent('Imported ' + recorder.frames.length + ' frames', '');
                               } catch (err) {
                                 logEvent('Import failed: invalid JSON', '');
                               }
                             };
                             reader.readAsText(file);
                           }

                           // === RECORDER EVENT LISTENERS ===
                           document.getElementById('recordBtn').addEventListener('click', function() {
                             if (recorder.recording) stopRecording();
                             else startRecording();
                           });

                           document.getElementById('playBtn').addEventListener('click', startPlayback);
                           document.getElementById('stopPlaybackBtn').addEventListener('click', stopPlayback);
                           document.getElementById('exportBtn').addEventListener('click', exportRecording);

                           document.getElementById('importBtn').addEventListener('click', function() {
                             document.getElementById('importFile').click();
                           });

                           document.getElementById('importFile').addEventListener('change', function(e) {
                             if (e.target.files.length > 0) {
                               importRecording(e.target.files[0]);
                               e.target.value = '';
                             }
                           });

                           // === HOOK INTO TICK ===
                           var _originalTick = tick;
                           tick = function() {
                             _originalTick();
                             if (recorder.recording && !paused) {
                               recorder.frames.push(captureFrame());
                               document.getElementById('frameCount').textContent = recorder.frames.length;
                               document.getElementById('playBtn').disabled = false;
                               document.getElementById('exportBtn').disabled = false;
                             }
                           };
                           ```

                           ---

                           When you've applied these, update this file with `[Kai] [timestamp] [ACK]` or `[DONE]` so I know you got it.

                           Good work on the concept - the architecture was right, just needed some defensive coding! 🔧

                           ---

                           ## Archive

                           (Previous threads can be moved here)
