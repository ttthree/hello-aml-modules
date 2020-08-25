using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Runtime.InteropServices;

namespace burn
{
    public class MemoryEater : IDisposable
    {
        private IntPtr _buffer;

        public MemoryEater(ulong numOfBytes)
        {
            _buffer = Marshal.AllocHGlobal((IntPtr)numOfBytes);
            for(int i=0; i < 10000; i++)
            {
                Marshal.WriteByte(_buffer, i, 0);
            }
        }

        public void Dispose()
        {
            Marshal.FreeHGlobal(_buffer);
        }

        public IntPtr Touch()
        {
            return _buffer;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            int numOfCores = int.Parse(args[0]);
            ulong numOfGBMemory = ulong.Parse(args[1]);
            int secondsToRun = int.Parse(args[2]);

            ulong bytes = numOfGBMemory * 1024 * 1024 * 1024;
            using (MemoryEater me = new MemoryEater(bytes))
            {
                Console.WriteLine("Eating {0}GB of memory, buffer size = {1}", numOfGBMemory, bytes);

                DateTime start = DateTime.Now;
                Parallel.For(0, numOfCores, index => {
                    Console.WriteLine("Hello World! {0} - {1}", index, Thread.CurrentThread.ManagedThreadId);

                    double x=945346346464.3453453453,y=7899.345345345,z=2343523523.242342342;
                    
                    int cnt = 0;
                    while (true)
                    {
                        y = Math.Sqrt(x) * Math.Sin(z) * Math.Pow(25,y);

                        if (++cnt % 100000 == 0)
                        {
                            DateTime now = DateTime.Now;
                            if ((now - start).TotalSeconds > secondsToRun)
                            {
                                Console.WriteLine("{0} seconds elapsed, exiting ...", secondsToRun);
                                Console.WriteLine("{0}", me.Touch());
                                break;
                            }
                        }
                    }
                });
            }
        }
    }
}
