# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.
from src.austral.configs import TARGET_COORDINATES, MODE
from src.austral.controller.quadrant_map import QuadrantMap
from src.austral.controller.threads.threadGlobalController import threadGlobalController
from src.austral.gps.lib.gps.direction_provider import DirectionProvider
from src.austral.gps.lib.trackmap.track_map import TrackMap
from src.austral.gps.lib.trackmap.xml_node_map_reader import XmlNodeMapReader
from src.austral.gps.threads.threadGPS import threadGPS
from src.austral.ultrasonic.frontal.threads.threadUltrasonics import threadUltrasonics

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
if __name__ == "__main__":
    import sys

    sys.path.insert(0, "../../..")
from src.templates.workerprocess import WorkerProcess


class processGlobalController(WorkerProcess):

    # ===================================== INIT =========================================
    def __init__(self, queueList):
        # self.track_mapping = TrackMap(XmlNodeMapReader.read("src/austral/gps/resources/xml_node_map.xml"))
        # self.direction_provider = DirectionProvider(self.track_mapping)
        self.queuesList = queueList
        super(processGlobalController, self).__init__(self.queuesList)

    # ===================================== STOP ==========================================
    def stop(self):
        """Function for stopping threads and the process."""
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processGlobalController, self).stop()

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads."""
        super(processGlobalController, self).run()

    # ===================================== INIT TH =================================
    def _init_threads(self):
        """Initializes the read and the write thread."""
        global_controller_thread = threadGlobalController(self.queuesList)
        self.threads.append(global_controller_thread)
