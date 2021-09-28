using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Etl.Summary
{
    class Program
    {
        static void Main(string[] args)
        {
            var python_path = @"D:\Programming\Upbit\Etl\EtlPrice\Etl.Highlight\env\Scripts\python.exe";
            var arg = @"D:\Programming\Upbit\Etl\EtlPrice\Etl.Highlight\summary.py";
            while (true)
            {
                
                System.Diagnostics.Process.Start(python_path, arg);
                Thread.Sleep(60 * 1000);


            }
        }
    }
}
