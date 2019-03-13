procedure Shit is
   Temperature, k : Integer;
begin
	k := 6;
   if Temperature >= 40*7 then
   	if Temperature < 50 then
   		k := 4;
   		k := k*k;
      else
         k := 3;
      end if;
   end if;
   k := 2;
end ;