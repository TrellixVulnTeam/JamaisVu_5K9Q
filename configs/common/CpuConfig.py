# Copyright (c) 2012, 2017-2018 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
from __future__ import absolute_import

from m5 import fatal
import m5.objects

def config_etrace(cpu_cls, cpu_list, options):
    if issubclass(cpu_cls, m5.objects.DerivO3CPU):
        # Assign the same file name to all cpus for now. This must be
        # revisited when creating elastic traces for multi processor systems.
        for cpu in cpu_list:
            # Attach the elastic trace probe listener. Set the protobuf trace
            # file names. Set the dependency window size equal to the cpu it
            # is attached to.
            cpu.traceListener = m5.objects.ElasticTrace(
                                instFetchTraceFile = options.inst_trace_file,
                                dataDepTraceFile = options.data_trace_file,
                                depWindowSize = 3 * cpu.numROBEntries)
            # Make the number of entries in the ROB, LQ and SQ very
            # large so that there are no stalls due to resource
            # limitation as such stalls will get captured in the trace
            # as compute delay. For replay, ROB, LQ and SQ sizes are
            # modelled in the Trace CPU.
            cpu.numROBEntries = 512
            cpu.LQEntries = 128
            cpu.SQEntries = 128
    else:
        fatal("%s does not support data dependency tracing. Use a CPU model of"
              " type or inherited from DerivO3CPU.", cpu_cls)


def config_extra(cpu_cls, cpu_list, options):
    if issubclass(cpu_cls, m5.objects.DerivO3CPU):
        if options.needsTSO == None or options.threatModel == "":
            fatal("Need to provide needsTSO and scheme to run simulation with DerivO3CPU")

        for cpu in cpu_list:
            cpu.needsTSO = options.needsTSO
            cpu.maxInsts = options.maxinsts
            cpu.HWName   = options.HWName
            cpu.threatModel = options.threatModel
            cpu.replayDetScheme = options.replayDetScheme
            cpu.sbHWStruct = options.sbHWStruct
            cpu.replayDetThreat = options.replayDetThreat

            cpu.maxReplays = options.maxReplays
            cpu.CCEnable = options.replayDetScheme == 'Counter'
            cpu.CCAssoc = options.CCAssoc
            cpu.CCSets = options.CCSets
            cpu.CCMissLatency = options.CCMissLatency
            cpu.CCIdeal = options.CCIdeal

            cpu.maxSBSize  = options.maxSBSize
            cpu.liftOnClear = options.liftOnClear
            cpu.projectedElemCnt = options.projectedElemCnt

            cpu.epochInfoPath = options.epoch_path
            cpu.epochSize     = options.epoch_size
            cpu.deleteOnRetire = options.deleteOnRetire
            cpu.activeRecords = options.activeRecords
            cpu.checkAllRecords = options.checkAllRecords
            cpu.counterSize = options.counterSize

            if cpu.threatModel == 'Unsafe':
                cpu.isSpectre = False
                cpu.isFuturistic = False
                cpu.HWName = 'Unsafe'
            elif cpu.threatModel == 'Spectre':
                cpu.isSpectre = True
                cpu.isFuturistic = False
                assert(cpu.HWName != 'Unsafe' and 'Unsafe CPU is vulnerable to Spectre')
            elif cpu.threatModel == 'Futuristic':
                cpu.isSpectre = True
                cpu.isFuturistic = True
                assert(cpu.HWName != 'Unsafe' and 'Unsafe CPU is vulnerable to Futuristic')
            else:
                fatal('Unknow threat model: {}'.format(cpu.threatModel))

            cpu.lowerSeqNum = options.dstate_start
            cpu.hasLowerBound = options.dstate_start != 0
            cpu.upperSeqNum = options.dstate_end
            cpu.hasUpperBound = options.dstate_end != 0
