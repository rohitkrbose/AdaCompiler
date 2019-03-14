procedure LoopDemo is
	type Car is record
     Identity       : Integer;
     Consumption    : Integer;
  end record;
   Count,k,Temperature : Integer;
   Independence_Day : Car;

begin
   Count := 1;
   	while Count < 5 loop           
      Count := Count * Count;
      Independence_Day.Identity := 24*Count*k;
   end loop;
   k := 7;
   
end;