procedure Shit is
   Temperature, k : Float;
begin
   if Temperature >= 40.0 OR k < 4.0 then
   	if Temperature < 50.0 then
   		k := 4.0;
   		-- k := 5.0 mod 7.0;
      else
         k := 3.0 + k;
      end if;
      k := 7.0;
   end if;
   k := 2.0;
   print (k);
end ;