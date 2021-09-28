using Newtonsoft.Json;
using RestSharp;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Etl.MarketPrice
{
    class Program
    {

        static string python_path = @"D:\Programming\Upbit\Etl\EtlPrice\Etl.Highlight\env\Scripts\python.exe";
        static string arg = @"D:\Programming\Upbit\Etl\EtlPrice\Etl.Highlight\candle.py";

     
        static void Main(string[] args)
        {

            //var market_url = $"https://api.upbit.com/v1/candles/minutes/1?market=KRW-BTC&count=1";
            //var client = new RestClient(market_url);
            //var request = new RestRequest();
            //var response = client.Get(request);
            //var market_price = JsonConvert.DeserializeObject<List<MarketPrice>>(response.Content);


            MarketList[] market_list = null;
            using (var dc = new CoinStarEntities())
            {
                market_list = dc.MarketList.Where(v=>v.market.StartsWith("KRW")).ToArray();
            }

            int count = 0;
            while (true)
            {
                Console.WriteLine("[Start At ",DateTime.Now,"]");
                Task.Run(()=> NewMethod(market_list, count));                
                Thread.Sleep(60 * 1000);
                count++;
                if (count % 3000 == 0)
                {
                    using (var dc = new CoinStarEntities())
                    {
                        var now = DateTime.Now;
                        var two_days_ago = now.AddDays(-2);
                        var old_datas = dc.MarketPrice.Where(v => v.regdate < two_days_ago);
                        dc.MarketPrice.RemoveRange(old_datas);
                        dc.SaveChanges();
                    }
                }
            }
        }

        private static int NewMethod(MarketList[] market_list, int count)
        {
            var a = DateTime.Now;
            List<MarketPrice> market_list_res = new List<MarketPrice>();
            //Parallel.ForEach()
            Parallel.ForEach(market_list, new ParallelOptions { MaxDegreeOfParallelism = 5 }, (l) =>
            {
                try
                {
                    Console.WriteLine($"==============={l.market}====================");
                    var market_url = $"https://api.upbit.com/v1/candles/minutes/1?market={l.market}&count=1" ;
                    var client = new RestClient(market_url);
                    var request = new RestRequest();
                    var response = client.Get(request);
                    Thread.Sleep(500);
                    var market_price = JsonConvert.DeserializeObject<List<MarketPrice>>(response.Content);
                    lock (market_list_res)
                    {
                        market_list_res.AddRange(market_price);
                    }
                }
                catch (Exception)
                {

                    throw;
                }


            });
            using (var dc = new CoinStarEntities())
            {
                dc.MarketPrice.AddRange(market_list_res);
                dc.PriceEtlLog.Add(new PriceEtlLog { regdate = DateTime.Now });

                dc.SaveChanges();

                System.Diagnostics.Process.Start(python_path, arg);
                var b = DateTime.Now;
                var r = (60) - ((b - a).TotalSeconds);
                //var remain = (int)(r);
                //Console.WriteLine($"{a} - {b} - {r} - {remain}");
                //Console.WriteLine("remain time ", remain); ;
                ////Thread.Sleep(remain*1000);
                //Console.WriteLine("=====================================1cycle===============================================");
                //count++;
                

            }

            return count;
        }
    }
}

