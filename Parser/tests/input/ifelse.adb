with Ada.Text_IO;
use  Ada.Text_IO;

procedure Shit is
   Temperature : Float;
begin
   if Temperature >= 40.0 then
      Put_Line ("Wow!");
      Put_Line ("It's extremely hot");
   elsif Temperature >= 30.0 then
      Put_Line ("It's hot");
   else
       Put_Line ("It's freezing");
   end if;
end Shit;