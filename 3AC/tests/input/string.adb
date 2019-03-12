with Ada.Text_IO, Ada.Integer_Text_IO;

procedure string is

   a : integer;
   str : array (1 .. 100) of character;
begin
   Scan_int(a);
   a := 1;
   for i in 1 .. a loop
      Scan_char(str(i));
   end loop;

   Print_newline(1);

   for j in 1 .. a loop
      Print_char(str(j));
   end loop;

   Print_newline(1);
   
end string;