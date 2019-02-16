with Ada.Text_IO;
use Ada.Text_IO;

procedure demo is
	squares: array (1 .. 10) of integer;
	begin
		for i in 1 .. 10 loop
			squares(i) := i * 2;
			i := i + 5;
		end loop;
	end demo;